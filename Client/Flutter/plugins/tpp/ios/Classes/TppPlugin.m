#import "TppPlugin.h"
#if __has_include(<tpp/tpp-Swift.h>)
#import <tpp/tpp-Swift.h>
#else
// Support project import fallback if the generated compatibility header
// is not copied when this plugin is created as a library.
// https://forums.swift.org/t/swift-static-libraries-dont-copy-generated-objective-c-header/19816
#import "tpp-Swift.h"
#endif

@implementation TppPlugin
+ (void)registerWithRegistrar:(NSObject<FlutterPluginRegistrar>*)registrar {
  [SwiftTppPlugin registerWithRegistrar:registrar];
}
@end
