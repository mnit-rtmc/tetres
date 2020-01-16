import 'package:flutter/material.dart';

class AppTheme {
  static final ThemeData light = new ThemeData(
    brightness: Brightness.light,
    primaryColorBrightness: Brightness.light,
    scaffoldBackgroundColor: Colors.white,
    primarySwatch: Colors.blue,
    buttonColor: Colors.blue,
    buttonTheme: ButtonThemeData(
        buttonColor: Colors.blue, textTheme: ButtonTextTheme.primary),
    primaryTextTheme: TextTheme(
      title: TextStyle(
        color: Colors.white,
      ),
    ),
    appBarTheme: AppBarTheme(
      iconTheme: IconThemeData(
        color: Colors.white,
      ),
      actionsIconTheme: IconThemeData(
        color: Colors.white,
      ),
    ),
  );

  static const maxWidthBoxConstraints = BoxConstraints(maxWidth: 500);
}
