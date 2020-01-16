import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:tetres/global/global.dart';

class AppDrawer extends StatefulWidget {
  AppDrawer({
    Key key,
    @required this.loginState,
    @required this.appDrawerItemCallback,
    @required this.getSelectedAppDrawerTile,
  }) : super(key: key);

  final LoginState loginState;
  final Function(GblListTile adt) appDrawerItemCallback;
  final GblListTile Function() getSelectedAppDrawerTile;

  @override
  _AppDrawerState createState() => _AppDrawerState();
}

class _AppDrawerState extends State<AppDrawer> {
  List<GblListTile> _appDrawerTiles = [];

  @override
  void initState() {
    super.initState();
    this._appDrawerTiles = Gbl.getAppDrawerTiles(widget.loginState);
  }

  void _onTileTap(GblListTile adt) {
    widget.appDrawerItemCallback(adt);
    Navigator.of(this.context).pop();
  }

  @override
  Widget build(BuildContext context) {
    var selectedAppDrawerTileTitle = widget.getSelectedAppDrawerTile().title;

    return new Drawer(
      child: new Column(
        mainAxisSize: MainAxisSize.max,
        children: <Widget>[
          new DrawerHeader(
            child: new Container(
              alignment: Alignment.center,
              child: Text(
                "TeTRES 2.0",
                textScaleFactor: 1.5,
                style: Theme.of(context).primaryTextTheme.title,
              ),
            ),
            decoration: BoxDecoration(
              color: Theme.of(context).primaryColor,
            ),
          ),
          new ListView.builder(
            shrinkWrap: true,
            itemCount: this._appDrawerTiles.length,
            itemBuilder: (ctx, index) {
              GblListTile adt = this._appDrawerTiles[index];
              return new ListTile(
                leading: new Icon(adt.icon),
                title: new Text(
                  adt.title,
                  style: adt.title == selectedAppDrawerTileTitle
                      ? DefaultTextStyle.of(context)
                          .style
                          .apply(color: Theme.of(context).primaryColor)
                      : null,
                ),
                onTap: () => this._onTileTap(adt),
              );
            },
          ),
        ],
      ),
    );
  }
}
