import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:tetres/admin_view/admin_home.dart';
import 'package:tetres/basic_view/basic_home.dart';
import 'package:tetres/global/global.dart';

import 'login_page.dart';

void main() {
  debugDefaultTargetPlatformOverride = TargetPlatform.fuchsia;
  runApp(App());
}

class App extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      home: PreLogin(),
    );
  }
}

class PreLogin extends StatefulWidget {
  PreLogin({
    Key key,
  }) : super(key: key);

  @override
  _PreLoginState createState() => _PreLoginState();
}

class _PreLoginState extends State<PreLogin> {
  LoginState _currentState = LoginState.none;

  void _loggedInCallback(LoginState loginState) {
    setState(() {
      this._currentState = loginState;
    });
  }

  void _loggedOutCallback() {
    setState(() {
      this._currentState = LoginState.none;
    });
  }

  @override
  Widget build(BuildContext context) {
    switch (this._currentState) {
      case LoginState.admin:
        return AdminHome(
          loggedOutCallback: this._loggedOutCallback,
        );
      case LoginState.basic:
        return BasicHome(
          loggedOutCallback: this._loggedOutCallback,
        );
      case LoginState.none:
        return LoginPage(loggedInCallback: this._loggedInCallback);
    }
    return LoginPage(loggedInCallback: this._loggedInCallback);
  }
}
