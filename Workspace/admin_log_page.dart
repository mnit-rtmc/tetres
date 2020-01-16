import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:tetres/api/api.dart';

class AdminLogPage extends StatefulWidget {
  AdminLogPage({
    Key key,
  }) : super(key: key);

  @override
  _AdminLogPageState createState() => _AdminLogPageState();
}

class _AdminLogPageState extends State<AdminLogPage> {
  Future<dynamic> _future;

  @override
  void initState() {
    super.initState();
//    this._future = Api.sendGet(endpoint: ApiEndPoints.actionLogList);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      child: FutureBuilder<dynamic>(
        future: this._future,
        builder: (BuildContext ctx, AsyncSnapshot<dynamic> snap) {
          if (snap.connectionState == ConnectionState.done) {
            if (snap.hasData) {
              return SingleChildScrollView(
                padding: EdgeInsets.all(8.0),
                child: Text("" + snap.data),
              );
            }
            return Text("Done No Data");
          }
          return Center(child: CircularProgressIndicator());
        },
      ),
    );
  }
}
