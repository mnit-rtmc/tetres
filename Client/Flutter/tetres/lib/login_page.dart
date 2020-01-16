import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:tetres/global/global.dart';

class LoginPage extends StatefulWidget {
  LoginPage({
    Key key,
    @required this.loggedInCallback,
  }) : super(key: key);

  final void Function(LoginState _preLoginStates) loggedInCallback;

  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  TextEditingController _userNameTxtCtrl = TextEditingController();
  TextEditingController _passphraseTxtCtrl = TextEditingController();

  var _enableLoginButton = false;
  var _loggingIn = false;
  var _titleText = "TeTRES 2.0";

  @override
  void initState() {
    super.initState();
    this._userNameTxtCtrl.addListener(this._checkEnableLoginButton);
    this._passphraseTxtCtrl.addListener(this._checkEnableLoginButton);
    this._userNameTxtCtrl.text = "admin";
    this._passphraseTxtCtrl.text = "admin";
  }

  @override
  void dispose() {
    this._userNameTxtCtrl.dispose();
    this._passphraseTxtCtrl.dispose();
    super.dispose();
  }

  Future<void> _onLoginButtonPress() async {
    setState(() {
      this._loggingIn = true;
    });

    await Future.delayed(Duration(seconds: 1), () {
      if (this._userNameTxtCtrl.text == "admin" &&
          this._passphraseTxtCtrl.text == "admin") {
        widget.loggedInCallback(LoginState.admin);
      }
    });
  }

  void _onContinueToBasicButtonPress() {
    widget.loggedInCallback(LoginState.basic);
  }

  void _checkEnableLoginButton() {
    var userName = this._userNameTxtCtrl.text;
    var pass = this._passphraseTxtCtrl.text;
    if (userName.length > 0 && pass.length > 0) {
      setState(() {
        this._enableLoginButton = true;
      });
    } else {
      setState(() {
        this._enableLoginButton = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Container(
          margin: EdgeInsets.all(24),
          constraints: AppTheme.maxWidthBoxConstraints,
          alignment: Alignment.center,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: !this._loggingIn
                ? <Widget>[
                    Text(
                      this._titleText,
                      textAlign: TextAlign.center,
                      textScaleFactor: 2.5,
                      style: TextStyle(color: Theme.of(context).primaryColor),
                    ),
                    TextField(
                      decoration: InputDecoration(labelText: "Username"),
                      controller: this._userNameTxtCtrl,
                      keyboardType: TextInputType.text,
                    ),
                    TextField(
                      decoration: InputDecoration(labelText: "Passphrase"),
                      obscureText: true,
                      controller: this._passphraseTxtCtrl,
                      keyboardType: TextInputType.text,
                    ),
                    Padding(
                      padding: const EdgeInsets.only(top: 16.0),
                      child: RaisedButton(
                        child: Text("Login"),
                        onPressed: this._enableLoginButton
                            ? this._onLoginButtonPress
                            : null,
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.only(top: 16.0),
                      child: RaisedButton(
                        child: Text("Continue To Basic TeTRES"),
                        onPressed: this._onContinueToBasicButtonPress,
                      ),
                    ),
                  ]
                : <Widget>[
                    Text(
                      this._titleText,
                      textAlign: TextAlign.center,
                      textScaleFactor: 2.5,
                      style: TextStyle(color: Theme.of(context).primaryColor),
                    ),
                    Container(
                      width: 50,
                      height: 50,
                      padding: EdgeInsets.all(8.0),
                      child: Center(child: CircularProgressIndicator()),
                    ),
                  ],
          ),
        ),
      ),
    );
  }
}
