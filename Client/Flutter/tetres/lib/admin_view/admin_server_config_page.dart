import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:intl/intl.dart';
import 'package:tetres/api/api.dart';
import 'package:tetres/global/global.dart';

class AdminServerConfigPage extends StatefulWidget {
  AdminServerConfigPage({
    Key key,
  }) : super(key: key);

  static const String dailyStartTime = "Daily Job Start Time";
  static const String weeklyStartTime = "Weekly Job Start Time";

  static const List<GblListTile> configTiles = [
    const GblListTile(title: dailyStartTime, icon: Icons.view_day),
  ];

  @override
  _AdminServerConfigPageState createState() => _AdminServerConfigPageState();
}

class _AdminServerConfigPageState extends State<AdminServerConfigPage> {
  Stream<ApiActionState> _stream;
  ApiSyscfg _syscfg;

  @override
  void initState() {
    super.initState();
    this._stream = this._getSyscfg();
  }

  Stream<ApiActionState> _getSyscfg() async* {
    yield ApiActionState.pending;
    Future.delayed(Duration(seconds: 2), () {});
    var reply = await Api.sendGet(endpoint: ApiEndPoints.systemConfigGet);
    if (reply?.body != null) {
      print("---> ${reply?.body}");
      yield ApiActionState.success;
      if ((this._syscfg = apiSyscfgFromJson(reply.body)) != null) {
        yield ApiActionState.success;
      } else {
        yield ApiActionState.fail;
      }
    } else {
      yield ApiActionState.fail;
    }
  }

  Stream<ApiActionState> _setSyscfg(TimeOfDay dailyStartTime) async* {
    yield ApiActionState.pending;
    Future.delayed(Duration(seconds: 2), () {});
    var now = DateTime.now();
    this._syscfg.obj.dailyJobStartTime = DateFormat.Hm().format(
      DateTime(now.year, now.month, now.day, dailyStartTime.hour,
          dailyStartTime.minute),
    );
    var reply = await Api.sendPost(
        endpoint: ApiEndPoints.systemConfigUpdate,
        bodyData: {"cfg": jsonEncode(this._syscfg.toJson()["obj"])});
    if (reply != null) {
      print("---> ${reply?.body}");
      String message;
      try {
        message = jsonDecode(reply?.body)["message"].toString();
      } catch (e) {
        print(e);
      }
      if (message != null && message == "success") {
        Api.sendGet(endpoint: ApiEndPoints.actionLogProceed);
        yield ApiActionState.success;
      } else {
        yield ApiActionState.fail;
      }
    } else {
      yield ApiActionState.fail;
    }
  }

  Future<void> _onTileTap(GblListTile glt) async {
    if (glt.title == AdminServerConfigPage.dailyStartTime) {
      var dailyStartTime = await showTimePicker(
        context: this.context,
        initialTime: TimeOfDay.now(),
      );
      if (dailyStartTime != null) {
        setState(() {
          this._stream = this._setSyscfg(dailyStartTime);
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      child: StreamBuilder<ApiActionState>(
        stream: this._stream,
        builder: (ctx, snap) {
          if (snap?.data != null) {
            switch (snap.data) {
              case ApiActionState.pending:
                return ApiActionWidget(
                    actionText: "Getting Current Config From Server");
              case ApiActionState.fail:
                return Container(
                  alignment: Alignment.center,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: <Widget>[
                      Text("Unable To Get Current Config From Server"),
                      RaisedButton.icon(
                        onPressed: () async {
                          this._stream = this._getSyscfg();
                        },
                        icon: Icon(Icons.refresh),
                        label: Text("Retry"),
                      ),
                    ],
                  ),
                );
              case ApiActionState.success:
                return Container(
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemCount: AdminServerConfigPage.configTiles.length,
                    itemBuilder: (ctx, index) {
                      GblListTile glt =
                          AdminServerConfigPage.configTiles[index];
                      return new ListTile(
                        leading: new Icon(glt.icon),
                        title: new Text(glt.title),
                        onTap: () {
                          this._onTileTap(glt);
                        },
                      );
                    },
                  ),
                );
            }
          }
          return Container();
        },
      ),
    );
  }
}

/*

switch (this._apiActionState) {
      case ApiActionState.pending:
        return ApiActionWidget();
      default:
        return Container(
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: Gbl.configTiles.length,
            itemBuilder: (ctx, index) {
              GblListTile glt = Gbl.configTiles[index];
              return new ListTile(
                isThreeLine: true,
                leading: new Icon(glt.icon),
                title: new Text(glt.title),
                subtitle: Text(this._apiSyscfg?.obj?.dailyJobStartTime ??
                    "Unable To Communicate With Server"),
                onTap: () => this._onTileTap(glt),
              );
            },
          ),
        );
    }
 */

//          DateTime.parse(
//              "${now.year.toString() + '-' + now.month.toString() + '-' + now.day.toString()} ${this._syscfg.obj.dailyJobStartTime}"),
