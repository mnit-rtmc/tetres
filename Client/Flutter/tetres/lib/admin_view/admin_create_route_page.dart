import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:tetres/api/api.dart';
import 'package:tetres/global/global.dart';

class AdminCreateRoutePage extends StatefulWidget {
  AdminCreateRoutePage({
    Key key,
  }) : super(key: key);

  @override
  _AdminCreateRoutePageState createState() => _AdminCreateRoutePageState();
}

class _AdminCreateRoutePageState extends State<AdminCreateRoutePage> {
  TextEditingController _routeNameTxtCtrl = TextEditingController();
  TextEditingController _routeDescriptionTxtCtrl = TextEditingController();
  Stream<ApiActionState> _stream;
  String _selectedCorridor;

  @override
  void initState() {
    super.initState();
    if (Gbl.gblApiInfra == null) {
      this._stream = Gbl.getInfra();
    } else {
      this._stream = this._infraPreviouslyLoaded();
    }
  }

  @override
  void dispose() {
    this._routeNameTxtCtrl.dispose();
    this._routeDescriptionTxtCtrl.dispose();
    super.dispose();
  }

  Stream<ApiActionState> _infraPreviouslyLoaded() async* {
    yield ApiActionState.success;
  }

  Future<void> _showSelectCorridorDialog() async {
    this._selectedCorridor = await showDialog(
      context: context,
      builder: (BuildContext context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20.0),
          ),
          child: Container(
            padding: EdgeInsets.all(24),
            constraints: AppTheme.maxWidthBoxConstraints,
            height: MediaQuery.of(this.context).size.height * .75,
            child: ListView.builder(
              itemCount: Gbl.gblApiInfra.corridorList.length,
              itemBuilder: (ctx, index) {
                return Card(
                  child: InkWell(
                    onTap: () {
                      Navigator.of(context)
                          .pop(Gbl.gblApiInfra.corridorList[index].name);
                    },
                    child: Padding(
                      padding: const EdgeInsets.all(8.0),
                      child:
                          Text("${Gbl.gblApiInfra.corridorList[index].name}"),
                    ),
                  ),
                );
              },
            ),
          ),
        );
      },
    );
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Create A New Route"),
      ),
      body: Center(
        child: Container(
          alignment: Alignment.center,
          margin: EdgeInsets.all(24),
          constraints: AppTheme.maxWidthBoxConstraints,
          child: StreamBuilder<ApiActionState>(
            stream: this._stream,
            builder: (ctx, snap) {
              if (snap?.hasData ?? false) {
                switch (snap.data) {
                  case ApiActionState.pending:
                    return ApiActionWidget();
                  case ApiActionState.fail:
                    return Container(
                      child: Text("Unable To Communicate With Server"),
                    );
                  case ApiActionState.success:
                    return Container(
                      alignment: Alignment.center,
                      child: ListView(
                        children: <Widget>[
                          //route name
                          //route description
                          //corridor
                          //start node
                          //end node
                          TextField(
                            decoration: InputDecoration(labelText: "Name"),
                            controller: this._routeNameTxtCtrl,
                            keyboardType: TextInputType.text,
                          ),
                          TextField(
                            decoration:
                                InputDecoration(labelText: "Description"),
                            controller: this._routeDescriptionTxtCtrl,
                            keyboardType: TextInputType.text,
                            maxLines: 5,
                          ),
                          Padding(
                            padding: const EdgeInsets.only(top: 8.0),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: <Widget>[
                                Text("${this._selectedCorridor ?? ""}"),
                                RaisedButton.icon(
                                  onPressed: _showSelectCorridorDialog,
                                  icon: Icon(Icons.list),
                                  label: Text("Select Corridor"),
                                ),
                              ],
                            ),
                          ),
                          Padding(
                            padding: const EdgeInsets.only(top: 8.0),
                            child: Card(
                              color: Colors.green,
                              margin: EdgeInsets.all(0),
                              child: Container(
                                  height: 175,
                                  alignment: Alignment.center,
                                  margin: EdgeInsets.all(8.0),
                                  padding: EdgeInsets.all(8.0),
                                  child: Text("Map View Here")),
                            ),
                          )
                        ],
                      ),
                    );
                }
              }
              return Container();
            },
          ),
        ),
      ),
    );
  }
}
