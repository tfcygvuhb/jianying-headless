import AppKit
import ApplicationServices
import CoreGraphics
import CryptoKit
import Foundation
import Vision

private let bundleID = "com.lemon.lvpro"
private let expectedWindowTitle = "剪映专业版"
private let schema = "build481-editor-identity-capture/v1"

private struct OCRItem: Codable {
    let text: String
    let confidence: Float
    let x: Double
    let y: Double
    let width: Double
    let height: Double
    let alternatives: [String]
}

private struct FailureRecord: Codable {
    let schema: String
    let status: String
    let capturedAt: String
    let code: String
    let detail: String
    let bundleID: String
    let pid: Int32?
    let cgWindowID: UInt32?
    let screenshot: String?
    let screenshotSHA256: String?
    let ocrItems: [OCRItem]?
}

private func die(_ message: String) -> Never {
    fputs("capture_identity: \(message)\n", stderr)
    exit(2)
}

private func nowISO8601() -> String {
    let formatter = ISO8601DateFormatter()
    formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
    return formatter.string(from: Date())
}

private func isInside(_ candidate: URL, _ parent: URL) -> Bool {
    let c = candidate.standardizedFileURL.pathComponents
    let p = parent.standardizedFileURL.pathComponents
    return c.count > p.count && Array(c.prefix(p.count)) == p
}

private func attribute(_ element: AXUIElement, _ key: String) -> CFTypeRef? {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, key as CFString, &value) == .success else { return nil }
    return value
}

private func stringAttribute(_ element: AXUIElement, _ key: String) -> String? {
    guard let raw = attribute(element, key) else { return nil }
    return raw as? String
}

private func axWindows(_ app: NSRunningApplication) -> [AXUIElement] {
    let root = AXUIElementCreateApplication(app.processIdentifier)
    guard let raw = attribute(root, kAXWindowsAttribute as String), let windows = raw as? [AXUIElement] else { return [] }
    return windows
}

private func axFrame(_ element: AXUIElement) -> CGRect? {
    guard let pRaw = attribute(element, kAXPositionAttribute as String),
          let sRaw = attribute(element, kAXSizeAttribute as String),
          CFGetTypeID(pRaw) == AXValueGetTypeID(), CFGetTypeID(sRaw) == AXValueGetTypeID() else { return nil }
    var point = CGPoint.zero
    var size = CGSize.zero
    guard AXValueGetValue(pRaw as! AXValue, .cgPoint, &point),
          AXValueGetValue(sRaw as! AXValue, .cgSize, &size),
          size.width > 0, size.height > 0 else { return nil }
    return CGRect(origin: point, size: size)
}

private func isFrontmost(_ app: NSRunningApplication) -> Bool {
    let root = AXUIElementCreateApplication(app.processIdentifier)
    return (attribute(root, kAXFrontmostAttribute as String) as? Bool) == true
}

private func regularEditor() throws -> NSRunningApplication {
    let apps = NSRunningApplication.runningApplications(withBundleIdentifier: bundleID)
        .filter { $0.activationPolicy == .regular && !$0.isTerminated }
    guard apps.count == 1, let app = apps.first else {
        throw CaptureError(code: "editor-pid-not-unique", detail: "expected one regular \(bundleID) process; found \(apps.map(\.processIdentifier))")
    }
    return app
}

private func editorWindow(_ app: NSRunningApplication) throws -> (AXUIElement, UInt32, CGRect) {
    guard isFrontmost(app) else {
        throw CaptureError(code: "editor-not-frontmost", detail: "the unique regular editor PID is not the frontmost application")
    }
    let windows = axWindows(app)
    guard windows.count == 1,
          let axWindow = windows.first,
          stringAttribute(axWindow, kAXRoleAttribute as String) == kAXWindowRole as String,
          stringAttribute(axWindow, kAXTitleAttribute as String) == expectedWindowTitle,
          let axRect = axFrame(axWindow) else {
        throw CaptureError(code: "ax-window-not-unique", detail: "expected one titled AXWindow with a readable frame; found \(windows.count)")
    }
    guard hasUniqueEditorMarker(app) else {
        throw CaptureError(code: "editor-marker-missing-or-ambiguous", detail: "MainTimeLineRoot must occur exactly once in the current AX tree")
    }

    let rawList = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
    let candidates = rawList.compactMap { info -> (UInt32, CGRect)? in
        guard (info[kCGWindowOwnerPID as String] as? NSNumber)?.int32Value == app.processIdentifier,
              (info[kCGWindowLayer as String] as? NSNumber)?.intValue == 0,
              info[kCGWindowName as String] as? String == expectedWindowTitle,
              let number = info[kCGWindowNumber as String] as? NSNumber,
              let bounds = info[kCGWindowBounds as String] as? [String: CGFloat],
              let x = bounds["X"], let y = bounds["Y"],
              let width = bounds["Width"], let height = bounds["Height"],
              width > 0, height > 0 else { return nil }
        let rect = CGRect(x: x, y: y, width: width, height: height)
        return (number.uint32Value, rect)
    }.filter { _, rect in framesMatch(rect, axRect) }
    guard candidates.count == 1, let chosen = candidates.first else {
        throw CaptureError(code: "cg-window-not-unique", detail: "expected one visible CGWindow matching the current PID, title and AX frame; found \(candidates.count)")
    }
    return (axWindow, chosen.0, chosen.1)
}

private func framesMatch(_ a: CGRect, _ b: CGRect) -> Bool {
    let tolerance: CGFloat = 3.0
    return abs(a.origin.x - b.origin.x) <= tolerance && abs(a.origin.y - b.origin.y) <= tolerance &&
        abs(a.width - b.width) <= tolerance && abs(a.height - b.height) <= tolerance
}

private func hasUniqueEditorMarker(_ app: NSRunningApplication) -> Bool {
    let root = AXUIElementCreateApplication(app.processIdentifier)
    var queue: [(AXUIElement, Int)] = [(root, 0)]
    var count = 0
    var visited = 0
    while !queue.isEmpty {
        let (element, depth) = queue.removeFirst()
        visited += 1
        if visited > 5000 { return false }
        if stringAttribute(element, kAXDescriptionAttribute as String) == "MainTimeLineRoot" { count += 1 }
        if count > 1 { return false }
        if depth < 24,
           let raw = attribute(element, kAXChildrenAttribute as String),
           let children = raw as? [AXUIElement] {
            queue.append(contentsOf: children.map { ($0, depth + 1) })
        }
    }
    return count == 1
}

private func assertUnlockedConsoleSession() throws {
    guard let state = CGSessionCopyCurrentDictionary() as? [String: Any],
          (state["kCGSSessionOnConsoleKey"] as? NSNumber)?.boolValue == true,
          (state["kCGSessionLoginDoneKey"] as? NSNumber)?.boolValue == true else {
        throw CaptureError(code: "console-session-unavailable", detail: "no active logged-in console session")
    }
    if let locked = state["CGSSessionScreenIsLocked"], (locked as? NSNumber)?.boolValue != false {
        throw CaptureError(code: "screen-locked", detail: "screen is locked")
    }
}

private struct CaptureError: Error {
    let code: String
    let detail: String
    init(code: String, detail: String) { self.code = code; self.detail = detail }
}

private func runScreencapture(windowID: UInt32, output: URL) throws {
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
    process.arguments = ["-l", String(windowID), "-x", output.path]
    let outPipe = Pipe(), errorPipe = Pipe()
    process.standardOutput = outPipe
    process.standardError = errorPipe
    do { try process.run() } catch {
        throw CaptureError(code: "screencapture-launch-failed", detail: String(describing: error))
    }
    process.waitUntilExit()
    let stdout = String(data: outPipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
    let stderr = String(data: errorPipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
    guard process.terminationStatus == 0,
          let attributes = try? FileManager.default.attributesOfItem(atPath: output.path),
          let size = attributes[.size] as? NSNumber, size.intValue > 0 else {
        throw CaptureError(code: "screencapture-failed", detail: "exit=\(process.terminationStatus); stdout=\(stdout); stderr=\(stderr)")
    }
}

private func sha256(_ url: URL) throws -> String {
    let data = try Data(contentsOf: url)
    return SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
}

private func runVision(_ imageURL: URL) throws -> [OCRItem] {
    guard let image = NSImage(contentsOf: imageURL),
          let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        throw CaptureError(code: "screenshot-unreadable", detail: "screencapture output is not a decodable image")
    }
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    request.recognitionLanguages = ["zh-Hans", "en-US"]
    do { try VNImageRequestHandler(cgImage: cgImage).perform([request]) }
    catch { throw CaptureError(code: "vision-failed", detail: String(describing: error)) }
    return (request.results ?? []).compactMap { observation -> OCRItem? in
        let candidates = observation.topCandidates(5)
        guard let top = candidates.first else { return nil }
        let box = observation.boundingBox
        return OCRItem(text: top.string, confidence: top.confidence,
                       x: Double(box.origin.x), y: Double(box.origin.y),
                       width: Double(box.width), height: Double(box.height),
                       alternatives: candidates.map(\.string))
    }.sorted {
        if abs($0.y - $1.y) > 0.006 { return $0.y > $1.y }
        return $0.x < $1.x
    }
}

private func normalizedLabel(_ text: String) -> String {
    text.trimmingCharacters(in: .whitespacesAndNewlines)
        .replacingOccurrences(of: "：", with: "")
        .replacingOccurrences(of: ":", with: "")
        .trimmingCharacters(in: .whitespacesAndNewlines)
}

private func labelCounts(_ items: [OCRItem]) -> [String: Int] {
    let required = ["草稿参数", "草稿名称", "保存位置"]
    var counts: [String: Int] = [:]
    for label in required {
        counts[label] = items.filter { normalizedLabel($0.text) == label }.count
    }
    return counts
}

private func writeJSON<T: Encodable>(_ value: T, to url: URL) throws {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
    try encoder.encode(value).write(to: url, options: .atomic)
}

private func ensureFreshOutputDirectory(_ rawPath: String, workRoot: URL) throws -> URL {
    let out = URL(fileURLWithPath: rawPath).standardizedFileURL
    guard isInside(out, workRoot) else {
        throw CaptureError(code: "output-outside-work", detail: "output directory must be inside repository work/")
    }
    let parent = out.deletingLastPathComponent()
    let resolvedParent = parent.resolvingSymlinksInPath()
    let resolvedWork = workRoot.resolvingSymlinksInPath()
    guard resolvedParent == resolvedWork || isInside(resolvedParent, resolvedWork) else {
        throw CaptureError(code: "output-parent-symlink-escape", detail: "resolved output parent escapes repository work/")
    }
    guard !FileManager.default.fileExists(atPath: out.path) else {
        throw CaptureError(code: "output-directory-exists", detail: "refusing to overwrite existing capture output")
    }
    try FileManager.default.createDirectory(at: out, withIntermediateDirectories: false)
    guard isInside(out.resolvingSymlinksInPath(), workRoot.resolvingSymlinksInPath()) else {
        throw CaptureError(code: "output-symlink-escape", detail: "resolved output directory escapes repository work/")
    }
    return out
}

private func failureRecord(code: String, detail: String, pid: Int32?, windowID: UInt32?, screenshot: URL?, items: [OCRItem]?) -> FailureRecord {
    let imageSHA = screenshot.flatMap { try? sha256($0) }
    return FailureRecord(schema: schema, status: "rejected", capturedAt: nowISO8601(),
                         code: code, detail: detail, bundleID: bundleID, pid: pid,
                         cgWindowID: windowID, screenshot: screenshot?.lastPathComponent,
                         screenshotSHA256: imageSHA, ocrItems: items)
}

private func capture(outputDirectory: URL) -> Int32 {
    let workRoot = URL(fileURLWithPath: #filePath).standardizedFileURL
        .deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("work")
    var pid: Int32?
    var windowID: UInt32?
    var screenshotURL: URL?
    var outputURL: URL?
    var ocrItems: [OCRItem]?
    do {
        outputURL = try ensureFreshOutputDirectory(outputDirectory.path, workRoot: workRoot)
        try assertUnlockedConsoleSession()
        guard AXIsProcessTrusted() else {
            throw CaptureError(code: "accessibility-unavailable", detail: "Accessibility permission is not granted")
        }
        let initialApp = try regularEditor()
        pid = initialApp.processIdentifier
        let (initialAXWindow, initialWindowID, initialFrame) = try editorWindow(initialApp)
        windowID = initialWindowID
        guard stringAttribute(initialAXWindow, kAXTitleAttribute as String) == expectedWindowTitle else {
            throw CaptureError(code: "window-title-changed", detail: "AX window title changed during preflight")
        }
        let imageURL = outputURL!.appendingPathComponent("editor-window.png")
        screenshotURL = imageURL
        try runScreencapture(windowID: initialWindowID, output: imageURL)

        // Re-resolve after capture so the saved image is not accepted if PID/window binding changed mid-capture.
        let currentApp = try regularEditor()
        guard currentApp.processIdentifier == initialApp.processIdentifier else {
            throw CaptureError(code: "pid-changed", detail: "regular editor PID changed during screenshot capture")
        }
        let (_, currentWindowID, currentFrame) = try editorWindow(currentApp)
        guard currentWindowID == initialWindowID && framesMatch(currentFrame, initialFrame) else {
            throw CaptureError(code: "window-binding-changed", detail: "frontmost main window ID or frame changed during screenshot capture")
        }
        let items = try runVision(imageURL)
        ocrItems = items
        let counts = labelCounts(items)
        let missingOrAmbiguous = counts.filter { $0.value != 1 }
        guard missingOrAmbiguous.isEmpty else {
            throw CaptureError(code: "required-ocr-labels-not-unique", detail: "required panel labels must each occur once: \(missingOrAmbiguous)")
        }
        // Recheck once more after Vision before creating the accepted envelope.
        let finalApp = try regularEditor()
        guard finalApp.processIdentifier == initialApp.processIdentifier,
              isFrontmost(finalApp),
              try editorWindow(finalApp).1 == initialWindowID else {
            throw CaptureError(code: "binding-changed-before-commit", detail: "PID/frontmost editor window binding changed before envelope write")
        }
        let imageSHA = try sha256(imageURL)
        let envelope: [String: Any] = [
            "schema": schema,
            "status": "captured",
            "capturedAt": nowISO8601(),
            "bundleID": bundleID,
            "pid": initialApp.processIdentifier,
            "cgWindowID": initialWindowID,
            "windowTitle": expectedWindowTitle,
            "windowBounds": ["x": initialFrame.origin.x, "y": initialFrame.origin.y,
                             "width": initialFrame.width, "height": initialFrame.height],
            "screenshot": imageURL.lastPathComponent,
            "screenshotSHA256": imageSHA,
            "vision": ["recognitionLevel": "accurate", "languages": ["zh-Hans", "en-US"],
                       "usesLanguageCorrection": false, "customWords": [],
                       "requiredLabelCounts": counts, "items": try JSONSerialization.jsonObject(with: JSONEncoder().encode(items))]
        ]
        let data = try JSONSerialization.data(withJSONObject: envelope, options: [.prettyPrinted, .sortedKeys])
        let evidenceURL = outputURL!.appendingPathComponent("identity-evidence.json")
        guard !FileManager.default.fileExists(atPath: evidenceURL.path) else {
            throw CaptureError(code: "evidence-file-exists", detail: "refusing to overwrite existing evidence JSON")
        }
        try data.write(to: evidenceURL, options: .atomic)
        print(String(data: data, encoding: .utf8)!)
        return 0
    } catch let error as CaptureError {
        if let outputURL {
            let record = failureRecord(code: error.code, detail: error.detail, pid: pid,
                                       windowID: windowID, screenshot: screenshotURL, items: ocrItems)
            try? writeJSON(record, to: outputURL.appendingPathComponent("capture-failure.json"))
        }
        fputs("capture_identity: \(error.code): \(error.detail)\n", stderr)
        return 2
    } catch {
        if let outputURL {
            let record = failureRecord(code: "unexpected-error", detail: String(describing: error), pid: pid,
                                       windowID: windowID, screenshot: screenshotURL, items: ocrItems)
            try? writeJSON(record, to: outputURL.appendingPathComponent("capture-failure.json"))
        }
        fputs("capture_identity: unexpected-error: \(error)\n", stderr)
        return 2
    }
}

guard CommandLine.arguments.count == 3, CommandLine.arguments[1] == "--out-dir" else {
    fputs("usage: capture_identity --out-dir <new-directory-inside-repository-work/>\n", stderr)
    exit(2)
}
exit(capture(outputDirectory: URL(fileURLWithPath: CommandLine.arguments[2]).standardizedFileURL))
