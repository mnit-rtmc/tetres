import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';

class ApiActionWidget extends StatefulWidget {
  ApiActionWidget({
    Key key,
    this.actionText,
  }) : super(key: key);

  final String actionText;

  @override
  _ApiActionWidgetState createState() => _ApiActionWidgetState();
}

class _ApiActionWidgetState extends State<ApiActionWidget> {
  @override
  Widget build(BuildContext context) {
    return Container(
      alignment: Alignment.center,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Text(widget.actionText != null
                ? "${widget.actionText}"
                : "Communicating With The TeTRES Server"),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: CircularProgressIndicator(),
          ),
        ],
      ),
    );
  }
}
