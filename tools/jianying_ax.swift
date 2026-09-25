import AppKit
import ApplicationServices
import Carbon.HIToolbox
import Darwin
import Foundation

struct Row: Codable {
    let path: String
    let role: String
    let title: String?
    let identifier: String?
    let description: String?
    let value: String?
    let enabled: Bool?
    let actions: [String]
    let x: Double?
    let y: Double?
    let width: Double?
    let height: Double?
}
struct Match { let element: AXUIElement; let row: Row }
func attribute(_ element: AXUIElement, _ name: String) -> CFTypeRef? {
    var value: CFTypeRef?
    return AXUIElementCopyAttributeValue(element, name as CFString, &value) == .success ? value : nil
}
func str(_ element: AXUIElement, _ name: String) -> String? {
    guard let value = attribute(element,name) else { return nil }
    if let value = value as? String { return value }
    if let value = value as? NSNumber { return value.stringValue }
    return nil
}
func actionNames(_ element: AXUIElement) -> [String] {
    var raw: CFArray?
    guard AXUIElementCopyActionNames(element,&raw) == .success else { return [] }
    return raw as? [String] ?? []
}
func snapshot(_ root: AXUIElement) -> [Match] {
    var result: [Match] = [], queue: [(AXUIElement,String,Int)] = [(root,"app",0)]
    while !queue.isEmpty && result.count < 1800 {
        let (element,path,depth)=queue.removeFirst()
        let rawValue=attribute(element,kAXValueAttribute)
        var p: CGPoint?, s: CGSize?
        if let raw=attribute(element,kAXPositionAttribute), CFGetTypeID(raw)==AXValueGetTypeID() { var v=CGPoint.zero; if AXValueGetValue(raw as! AXValue,.cgPoint,&v){p=v} }
        if let raw=attribute(element,kAXSizeAttribute), CFGetTypeID(raw)==AXValueGetTypeID() { var v=CGSize.zero; if AXValueGetValue(raw as! AXValue,.cgSize,&v){s=v} }
        let row=Row(path:path,role:str(element,kAXRoleAttribute) ?? "",title:str(element,kAXTitleAttribute),identifier:str(element,kAXIdentifierAttribute),description:str(element,kAXDescriptionAttribute),value:(rawValue as? String) ?? (rawValue as? NSNumber)?.stringValue,enabled:attribute(element,kAXEnabledAttribute) as? Bool,actions:actionNames(element),x:p.map{Double($0.x)},y:p.map{Double($0.y)},width:s.map{Double($0.width)},height:s.map{Double($0.height)})
        result.append(Match(element:element,row:row))
        if depth < 18, let kids=attribute(element,kAXChildrenAttribute) as? [AXUIElement] { for (i,kid) in kids.enumerated(){queue.append((kid,"\(path)/\(i)",depth+1))} }
    }
    if !queue.isEmpty { fputs("AX tree exceeded the complete snapshot limit\n",stderr); exit(18) }
    return result
}
func appForBundle(_ bundleID: String) -> NSRunningApplication {
    let candidates=NSRunningApplication.runningApplications(withBundleIdentifier:bundleID).filter{$0.activationPolicy == .regular && !$0.isTerminated}
    guard candidates.count == 1 else { fputs("expected one regular process for \(bundleID), found \(candidates.count)\n",stderr); exit(4) }
    return candidates[0]
}
func select(_ rows:[Match],_ role:String,_ field:String,_ value:String)->Match {
    let candidates=rows.filter{m in m.row.role==role && (field=="title" ? m.row.title==value : field=="identifier" ? m.row.identifier==value : field=="description" ? m.row.description==value : field=="value" ? m.row.value==value : false)}
    guard candidates.count==1 else { fputs("selector role=\(role) \(field)=\(value) matched \(candidates.count), expected exactly one\n",stderr); exit(5) }
    return candidates[0]
}
func waitFor(_ app:NSRunningApplication, _ field:String,_ value:String,_ role:String?=nil,_ seconds:Double=8)->[Match]? {
    let root=AXUIElementCreateApplication(app.processIdentifier), until=Date().addingTimeInterval(seconds)
    repeat {
        let rows=snapshot(root)
        let matches=rows.filter{m in (role == nil || m.row.role==role!) && (field=="title" ? m.row.title==value : field=="identifier" ? m.row.identifier==value : field=="description" ? m.row.description==value : field=="value" ? m.row.value==value : false)}
        if matches.count == 1 { return rows }
        if matches.count > 1 { fputs("post-action state is ambiguous\n",stderr); exit(20) }
        Thread.sleep(forTimeInterval:0.25)
    } while Date()<until
    return nil
}
func activateAndConfirm(_ app:NSRunningApplication) {
    let root=AXUIElementCreateApplication(app.processIdentifier)
    let until=Date().addingTimeInterval(8)
    while Date()<until {
        _=app.activate()
        _=AXUIElementSetAttributeValue(root,kAXFrontmostAttribute as CFString,kCFBooleanTrue)
        if attribute(root,kAXFrontmostAttribute) as? Bool == true { return }
        Thread.sleep(forTimeInterval:0.2)
    }
    fputs("target app did not become AXFrontmost\n",stderr); exit(17)
}
func sendCommandS(_ app:NSRunningApplication) {
    let root=AXUIElementCreateApplication(app.processIdentifier), rows=snapshot(root)
    _=select(rows,"AXStaticText","description","MainTimeLineRoot")
    if let window=rows.first(where:{$0.row.role=="AXWindow"}), !window.row.actions.contains(kAXRaiseAction as String) { fputs("window cannot be raised\n",stderr); exit(6) }
    if let window=rows.first(where:{$0.row.role=="AXWindow"}) { _=AXUIElementPerformAction(window.element,kAXRaiseAction as CFString) }
    activateAndConfirm(app)
    let down=CGEvent(keyboardEventSource:nil,virtualKey:UInt16(kVK_ANSI_S),keyDown:true)!,up=CGEvent(keyboardEventSource:nil,virtualKey:UInt16(kVK_ANSI_S),keyDown:false)!
    down.flags=[.maskCommand];up.flags=[.maskCommand];down.post(tap:.cghidEventTap);up.post(tap:.cghidEventTap)
    guard waitFor(app,"description","MainTimeLineRoot","AXStaticText") != nil else { fputs("editor state lost after Command+S\n",stderr); exit(7) }
    print("saved: Cmd+S; MainTimeLineRoot remained visible")
}
func quitNormally(_ app:NSRunningApplication) {
    let root=AXUIElementCreateApplication(app.processIdentifier), rows=snapshot(root)
    let item=select(rows,"AXMenuItem","identifier","onAppQuitTriggered:")
    guard item.row.enabled != false && item.row.actions.contains(kAXPressAction as String) else { fputs("normal Quit action unavailable\n",stderr); exit(8) }
    guard AXUIElementPerformAction(item.element,kAXPressAction as CFString) == .success else { fputs("AX menu Quit failed\n",stderr); exit(9) }
    let until=Date().addingTimeInterval(12)
    while Date()<until && !app.isTerminated && kill(app.processIdentifier,0)==0 { Thread.sleep(forTimeInterval:0.25) }
    let gone = app.isTerminated || (kill(app.processIdentifier,0) != 0 && errno == ESRCH)
    guard gone else { fputs("main editor process stayed alive after normal Quit\n",stderr); exit(10) }
    print("quit: AXMenuItem identifier=onAppQuitTriggered:, pid=\(app.processIdentifier) terminated")
}
guard AXIsProcessTrusted(),CommandLine.arguments.count>=3 else { fputs("usage: jianying_ax check|set|click|save|quit <bundle-id> [...]; AX trust required\n",stderr);exit(2) }
let command=CommandLine.arguments[1],bundleID=CommandLine.arguments[2]
let expectedBundle="com.lemon.lvpro"
guard bundleID==expectedBundle else {fputs("unexpected bundle id\n",stderr);exit(3)}
if command=="quit" { let app=appForBundle(bundleID);quitNormally(app);exit(0) }
if command=="check" {
    guard CommandLine.arguments.count==6 else {fputs("check needs role field exact-value\n",stderr);exit(2)}
    let app=appForBundle(bundleID), rows=snapshot(AXUIElementCreateApplication(app.processIdentifier))
    let _=select(rows,CommandLine.arguments[3],CommandLine.arguments[4],CommandLine.arguments[5])
    print("unique: \(CommandLine.arguments[3]) \(CommandLine.arguments[4])=\(CommandLine.arguments[5])")
    exit(0)
}
let app=appForBundle(bundleID)
if command=="save" { sendCommandS(app);exit(0) }
guard CommandLine.arguments.count >= 6 else {fputs("set|click args: role field exact-value [new-value | expected-role expected-field expected-value]\n",stderr);exit(2)}
guard ["set","click"].contains(command) else {fputs("unknown command\n",stderr);exit(2)}
if command=="click" {
    activateAndConfirm(app)
}
let root=AXUIElementCreateApplication(app.processIdentifier), rows=snapshot(root)
let role=CommandLine.arguments[3],field=CommandLine.arguments[4],value=CommandLine.arguments[5],match=select(rows,role,field,value)
if command=="set" {
    guard CommandLine.arguments.count==7 else {fputs("set needs new-value\n",stderr);exit(2)}
    let newValue=CommandLine.arguments[6]
    guard AXUIElementSetAttributeValue(match.element,kAXValueAttribute as CFString,newValue as CFString) == .success,
          str(match.element,kAXValueAttribute)==newValue else {fputs("AXSetValue/readback failed\n",stderr);exit(11)}
    print("set/readback: \(role) \(field)=\(value) value=\(newValue)");exit(0)
}
if command=="click" {
    guard CommandLine.arguments.count==9 else {fputs("click needs expected-role expected-field expected-value\n",stderr);exit(2)}
    let expectedRole=CommandLine.arguments[6],expectedField=CommandLine.arguments[7],expectedValue=CommandLine.arguments[8]
    let before=rows.filter{m in m.row.role==expectedRole && (expectedField=="title" ? m.row.title==expectedValue : expectedField=="identifier" ? m.row.identifier==expectedValue : expectedField=="description" ? m.row.description==expectedValue : expectedField=="value" ? m.row.value==expectedValue : false)}
    guard before.isEmpty else {fputs("post-action state was already present before click\n",stderr);exit(19)}
    if match.row.actions.contains(kAXPressAction as String) {
        guard match.row.enabled != false,AXUIElementPerformAction(match.element,kAXPressAction as CFString) == .success else {fputs("AXPress failed\n",stderr);exit(13)}
    } else {
        guard let x=match.row.x,let y=match.row.y,let w=match.row.width,let h=match.row.height,w>0,h>0 else {fputs("element has no live AX frame\n",stderr);exit(14)}
        let point=CGPoint(x:x+w/2,y:y+h/2)
        for kind in [CGEventType.leftMouseDown,.leftMouseUp] { guard let event=CGEvent(mouseEventSource:nil,mouseType:kind,mouseCursorPosition:point,mouseButton:.left) else {fputs("click event creation failed\n",stderr);exit(15)};event.post(tap:.cghidEventTap) }
    }
    guard let after=waitFor(app,expectedField,expectedValue,expectedRole) else {fputs("post-action state was not observed: \(expectedRole) \(expectedField)=\(expectedValue)\n",stderr);exit(16)}
    print("click/readback: unique \(role) \(field)=\(value); post-state \(expectedRole) \(expectedField)=\(expectedValue); rows=\(after.count)");exit(0)
} else {fputs("unknown command \(command)\n",stderr);exit(2)}
