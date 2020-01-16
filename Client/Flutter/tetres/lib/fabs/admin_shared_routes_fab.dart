import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:tetres/admin_view/admin_create_route_page.dart';

class AdminSharedRoutesFab extends StatelessWidget {
  AdminSharedRoutesFab({
    Key key,
    @required this.context,
  }) : super(key: key);
  final BuildContext context;

  void _showAdminCreateRoutePage() {
    Navigator.of(this.context).push(
      MaterialPageRoute(
        builder: (BuildContext context) => AdminCreateRoutePage(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton(
      child: Icon(Icons.add),
      onPressed: this._showAdminCreateRoutePage,
    );
  }
}
