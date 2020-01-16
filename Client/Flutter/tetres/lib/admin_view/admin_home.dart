import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:tetres/app_drawer/app_drawer.dart';
import 'package:tetres/fabs/admin_shared_routes_fab.dart';
import 'package:tetres/global/global.dart';
import 'package:tetres/shared_view/shared_routes_page.dart';

import 'admin_server_config_page.dart';

class AdminHome extends StatefulWidget {
  AdminHome({
    Key key,
    @required this.loggedOutCallback,
  }) : super(key: key);

  final void Function() loggedOutCallback;

  @override
  _AdminHomeState createState() => _AdminHomeState();
}

class _AdminHomeState extends State<AdminHome> {
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
    switch (this._selectedAppDrawerTile.title) {
      case (Gbl.appDrawerRoutes):
        return SharedRoutesPage(
          loginState: LoginState.admin,
        );
      case (Gbl.appDrawerServerConfig):
        return AdminServerConfigPage();
    }
    return Container();
  }

  Widget _getFabWidget() {
    switch (this._selectedAppDrawerTile.title) {
      case (Gbl.appDrawerRoutes):
        return AdminSharedRoutesFab(
          context: this.context,
        );
      case (Gbl.appDrawerServerConfig):
        return null;
    }
    return null;
  }

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("TeTRES 2.0 Admin"),
      ),
      drawer: AppDrawer(
        loginState: LoginState.admin,
        appDrawerItemCallback: this._appDrawerItemCallback,
        getSelectedAppDrawerTile: this.getSelectedAppDrawerTile,
      ),
      body: this._getBodyWidget(),
      floatingActionButton: this._getFabWidget(),
    );
  }
}
