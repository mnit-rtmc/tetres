import 'dart:async';

import 'package:flutter/services.dart';

class Tpp {
  static const MethodChannel _channel = const MethodChannel('tpp');

  static Future<String> get platformVersion async {
    final String version = await _channel.invokeMethod('getPlatformVersion');
    return version;
  }

  static Future<String> get getCurrentDirectory async {
    final String version = await _channel.invokeMethod('getCurrentDirectory');
    return version;
  }
}
