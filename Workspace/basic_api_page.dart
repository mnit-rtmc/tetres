import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:tetres/api/api.dart';

class ApiPage extends StatefulWidget {
  ApiPage({
    Key key,
  }) : super(key: key);

  @override
  _ApiPageState createState() => _ApiPageState();
}

class _ApiPageState extends State<ApiPage> {
  Future<dynamic> _future;

  @override
  void initState() {
    super.initState();
    this._future = Api.sendGet(endpoint: ApiEndPoints.userApiInfo);
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
