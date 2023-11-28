import 'package:flutter/material.dart';
// https://pub.dev/packages/logger
import 'package:logger/logger.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

class Ledstrip {
  Logger? logger;
  String _endpoint = "";
  Map<String, dynamic>? _metaData;

  @override
  String toString() {
    return name();
  }

  void setEndpoint(String endpoint) {
    _endpoint=endpoint;
  }

  void setLogger(Logger logger) {
    this.logger=logger;
  }

  String name() {
    // Return the name of the ledstrip.  If we don't have the name, then return the endpoint URL.
    // Return an empty string if we have neither:
    return _metaData?['light']['name'] ?? _endpoint ?? "";
  }

  bool isOn() {
    // Return the state of the ledstrip (on == true; off == false).
    // Return false if we don't have the metadata:
    return _metaData?['light']['state'] ?? false;
  }

  int getBrightness() {
    return _metaData?['light']['brightness'] ?? 0;
  }
  void setBrightness(int value) {
    _metaData?['light']['brightness'] = value;
  }

  Color getColor() {
    int r = _metaData?['light']['color']['red'];
    int g = _metaData?['light']['color']['green'];
    int b = _metaData?['light']['color']['blue'];
    return Color.fromRGBO(r, g, b, 1.0);
  }
  void setColor(Color color) {
    _metaData?['light']['color']['red'] = color.red;
    _metaData?['light']['color']['green'] = color.green;
    _metaData?['light']['color']['blue'] = color.blue;
  }

  // Reset the colors to plain white:
  void reset() {
    _metaData?['light']['brightness'] = 128;
    setColor(Color.fromRGBO(255, 255, 255, 1.0));
  }

  // Call the Ledstrip API asynchronously to get metadata:
  Future<void> getMetadata({required Function callback}) async {
    logger?.d('API call to get metadata');
    http.Response response = await http.get(Uri.parse(_endpoint));
    if (response.statusCode == 200) {
      logger?.d("Received data: " + response.body);
      _metaData = jsonDecode(response.body);
      logger?.i("Ledstrip name: " + _metaData?['light']['name']);
      // We got new data from the ledstrip.  Run the callback function to update data in the UI:
      callback();
    } else {
      logger?.e("Failed to get ledstrip details");
      throw Exception("Failed to get ledstrip details");
    }
  }

  // Call the Ledstrip API asynchronously to update its data:
  Future<void> updateMetadata({bool toggle = true, required Function callback}) async {
    String behavior = "Default";   // "Default" or "Christmass"
    logger?.d('API call to update the ledstrip');
    String data = jsonEncode(<String, dynamic>{
      "action": "update",
      "toggle": toggle,
      "behavior": behavior,
      "led-count": _metaData?['light']['led-count'],
      "brightness": _metaData?['light']['brightness'],
      "color": {
        "red": _metaData?['light']['color']['red'],
        "green": _metaData?['light']['color']['green'],
        "blue": _metaData?['light']['color']['blue'],
        "white": _metaData?['light']['color']['white']
      }
    });
    logger?.d("Sending data: " + data);
    http.Response response = await http.post(
      Uri.parse(_endpoint),
      headers: <String, String>{
        "Content-Type": "application/json; charset=UTF-8",
      },
      body: data,
    );
    if (response.statusCode == 200) {
      logger?.d(response.body);
      // We can assume that the ledstrip data was updated successfully.
      // Now run the callback function, which will refresh the metadata that app has and update the UI:
      callback();
    } else {
      logger?.e("Failed to update ledstrip details");
      logger?.e(response.body);
      throw Exception("Failed to update ledstrip details");
    }
  }
}
