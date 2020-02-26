import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:tetres/tetres_admin/admin_home.dart';
import 'package:tetres/tetres_basic/basic_home.dart';
import 'package:tetres/tetres_global/global.dart';

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
  PreLoginStates _currentState = PreLoginStates.loggedOut;

  void _loggedInCallback(PreLoginStates loginState) {
    setState(() {
      this._currentState = loginState;
    });
  }

  void _loggedOutCallback() {
    setState(() {
      this._currentState = PreLoginStates.loggedOut;
    });
  }

  @override
  Widget build(BuildContext context) {
    switch (this._currentState) {
      case PreLoginStates.loggedInAdmin:
        return AdminHome(
          loggedOutCallback: this._loggedOutCallback,
        );
      case PreLoginStates.loggedInBasic:
        return BasicHome(
          loggedOutCallback: this._loggedOutCallback,
        );
      case PreLoginStates.loggedOut:
        return LoginPage(loggedInCallback: this._loggedInCallback);
    }
    return LoginPage(loggedInCallback: this._loggedInCallback);
  }
}

class HomePage extends StatefulWidget {
  HomePage({
    Key key,
  }) : super(key: key);

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  Future<String> _future;

  Future<String> _tryConnect() async {
    http.Response res;
    await Future.delayed(Duration(seconds: 1), () async {
      res = await http.get("http://localhost:5000/tetres/");
    });

    return "TeTRES SERVER REPLIED WITH ${res.contentLength.toString()} BYTES";
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("TeTRES 2.0"),
      ),
      body: Container(
        alignment: Alignment.center,
        child: this._future == null
            ? Container()
            : FutureBuilder<String>(
                future: this._future,
                builder: (BuildContext ctx, AsyncSnapshot<String> snap) {
                  if (snap.connectionState == ConnectionState.done) {
                    if (snap.hasData) {
                      return Text("" + snap.data);
                    }
                    return Text("Done No Data");
                  }
                  return Center(child: CircularProgressIndicator());
                },
              ),
      ),
      floatingActionButton: FloatingActionButton(
        child: Icon(this._future == null ? Icons.power : Icons.stop),
        onPressed: () => setState(() {
          if (this._future == null) {
            this._future = this._tryConnect();
          } else {
            this._future = null;
          }
        }),
      ),
    );
  }
}
