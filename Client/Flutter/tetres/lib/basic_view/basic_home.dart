import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:tetres/app_drawer/app_drawer.dart';
import 'package:tetres/global/global.dart';

class BasicHome extends StatefulWidget {
  BasicHome({
    Key key,
    @required this.loggedOutCallback,
  }) : super(key: key);
  final void Function() loggedOutCallback;

  @override
  _BasicHomeState createState() => _BasicHomeState();
}

class _BasicHomeState extends State<BasicHome> {
  GblListTile _selectedAppDrawerTile = Gbl.appDrawerTilesAdmin[0];

  GblListTile getSelectedAppDrawerTile() => this._selectedAppDrawerTile;

  void _appDrawerItemCallback(GblListTile adt) {
    if (adt.title == Gbl.appDrawerBackToLogin) {
      widget.loggedOutCallback();
    }
    setState(() {
      this._selectedAppDrawerTile = adt;
    });
  }

  Widget _getBodyWidget() {
    return Container();
  }

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          title: Text("TeTRES 2.0 Basic"),
        ),
        drawer: AppDrawer(
          loginState: LoginState.basic,
          appDrawerItemCallback: this._appDrawerItemCallback,
          getSelectedAppDrawerTile: this.getSelectedAppDrawerTile,
        ),
        body: this._getBodyWidget());
  }
}
