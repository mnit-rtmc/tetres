import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:tetres/api/api.dart';
import 'package:tetres/global/global.dart';

class SharedRoutesPage extends StatefulWidget {
  SharedRoutesPage({
    Key key,
    @required this.loginState,
  }) : super(key: key);

  final LoginState loginState;

  @override
  _SharedRoutesPageState createState() => _SharedRoutesPageState();
}

class _SharedRoutesPageState extends State<SharedRoutesPage> {
  Stream<ApiActionState> _stream;
  List<ApiRouteListElement> _routes;

  @override
  void initState() {
    super.initState();
    this._stream = this._getRoutes();
  }

  Stream<ApiActionState> _getRoutes() async* {
    yield ApiActionState.pending;
    Future.delayed(Duration(seconds: 2), () {});
    var reply = await Api.sendGet(endpoint: ApiEndPoints.adminListRoutes);
    if (reply?.body != null) {
      if ((this._routes = apiRouteListFromJson(reply.body)?.obj?.list) !=
          null) {
        yield ApiActionState.success;
      } else {
        yield ApiActionState.fail;
      }
    } else {
      yield ApiActionState.fail;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      child: StreamBuilder<ApiActionState>(
        stream: this._stream,
        builder: (ctx, snap) {
          if (snap?.hasData ?? false) {
            print("---> ${snap.data}");
            switch (snap.data) {
              case ApiActionState.pending:
                return ApiActionWidget(
                    actionText: "Getting Routes From Server");
              case ApiActionState.success:
                return Container(
                  child: new ListView.builder(
                    shrinkWrap: true,
                    itemCount: this._routes.length,
                    itemBuilder: (ctx, index) {
                      ApiRouteListElement rle = this._routes[index];
                      return new ListTile(
                        leading: new Icon(Icons.drive_eta),
                        title: new Text("${rle.name}"),
                        subtitle: new Text("${rle.corridor}"),
                      );
                    },
                  ),
                );
              case ApiActionState.fail:
                return Container(
                  alignment: Alignment.center,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: <Widget>[
                      Text("Unable To Get Routes From Server"),
                      RaisedButton.icon(
                        onPressed: () async {
                          this._stream = this._getRoutes();
                        },
                        icon: Icon(Icons.refresh),
                        label: Text("Retry"),
                      )
                    ],
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
