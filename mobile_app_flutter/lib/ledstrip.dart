import 'package:flutter/material.dart';
// https://pub.dev/packages/logger
import 'package:logger/logger.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

class Ledstrip {
  Logger? logger;
  String _endpoint = "";
  Map<String, dynamic>? _metaData = {};
  String _errors = "";

  @override
  String toString() {
    return name;
  }

  void setLogger(Logger logger) {
    this.logger = logger;
  }

  String get name {
    // Return the name of the ledstrip.
    // If we don't have the name, then return "Not Available":
    return _metaData?['light']['name'] ?? "N/A";
  }

  set name(String value) {
// ToDo: do validation!
    _metaData?['light']['name'] = value;
  }

  String get endpoint {
    return _endpoint;
  }

  set endpoint(String value) {
// ToDo: do validation!
    _endpoint = value;
  }

  // Get a list of all the behaviors this ledstrip supports (pulled from API):
  List<String> get behaviorNames {
    try {
      // The JSON list of strings is returned as a List<dynamic>.
      // We need to convert it to a List of Strings:
      return List<String>.from(_metaData?['behaviors'] as List);
      // This works too by converting each element individually to a string:
      // (I find it less readable though)
      // return (_metaData?['behaviors'] as List).map((item) => item as String).toList();
    } on Exception {
      // Not all ledstrips support this in their API:
      return ["None"];
    }
  }

  // Get the name of the active behavior the ledstrip is configured with:
  String get behaviorName {
    return _metaData?['light']['behavior'] ?? "Default";
  }

  // Change the active behavior in the ledstrip:
  set behaviorName(String value) {
    if (_metaData?['behaviors'].contains(value)) {
      _metaData?['light']['behavior'] = value;
    } else {
      throw Exception("The program name must be one of the supported values! (${behaviorNames.join(", ")}");
    }
  }

  int get brightness {
    return _metaData?['light']['brightness'] ?? 1;
  }

  set brightness(int value) {
    if (value < 0 || value > 255) {
      throw Exception(["The brightness value must be between 0 and 255!"]);
    }
    _metaData?['light']['brightness'] = value;
  }

  Color get color {
    int r = _metaData?['light']['color']['red'] ?? 0;
    int g = _metaData?['light']['color']['green'] ?? 0;
    int b = _metaData?['light']['color']['blue'] ?? 0;
    return Color.fromRGBO(r, g, b, 1.0);
  }

  set color(Color color) {
    _metaData?['light']['color']['red'] = color.red;
    _metaData?['light']['color']['green'] = color.green;
    _metaData?['light']['color']['blue'] = color.blue;
  }

  bool isOn() {
    // Return the state of the ledstrip (on == true; off == false).
    // Return false if we don't have the metadata:
    return _metaData?['light']['state'] ?? false;
  }

  // Reset the colors to plain white:
  void reset() {
    _metaData?['light']['brightness'] = 90;
    color = Color.fromRGBO(255, 255, 255, 1.0);
  }

  // Check to see if we have metadata for the ledstrip.
  // This is used to check if we have a valid ledstrip.
  bool hasMetadata() {
    bool retVal = true;
    if (_errors != "" || (_metaData?.isEmpty ?? true)) retVal = false;
    return retVal;
  }

  bool get hasErrors {
    return _errors != "";
  }

  String get errors {
    return _errors;
  }

  // Call the Ledstrip API asynchronously to get metadata:
  Future<void> getMetadata({required Function callback}) async {
    logger?.d('API call to get metadata');
    _metaData = {};
    _errors = "";
    try {
      http.Response response = await http.get(Uri.parse(_endpoint));
      if (response.statusCode == 200) {
        logger?.d("Received data: $response.body");
        _metaData = jsonDecode(response.body);
        if (_metaData?['errors'] != null) {
          // The API call returned errors!
          _errors = "Failed to get ledstrip details!\n${_metaData?['errors']}";
        }
        logger?.i("Ledstrip name: $_metaData?['light']['name']");
      } else {
        logger?.e("Failed to get ledstrip details");
        _errors = "Failed to get ledstrip details";
      }
    } catch (err) {
      // There was a network issue:
      _errors = err.toString();
    }
    // We got new data from the ledstrip (or errors).
    // Run the callback function to update data in the UI:
    callback(_errors);
  }

  // Call the Ledstrip API asynchronously to update its data:
  Future<void> updateMetadata({bool toggle = true, required Function callback}) async {
    logger?.d('API call to update the ledstrip');
    String data = jsonEncode(<String, dynamic>{
      "action": "update",
      "toggle": toggle,
      "behavior": _metaData?['light']['behavior'],
      "led-count": _metaData?['light']['led-count'],
      "brightness": _metaData?['light']['brightness'],
      "color": {"red": _metaData?['light']['color']['red'], "green": _metaData?['light']['color']['green'], "blue": _metaData?['light']['color']['blue'], "white": _metaData?['light']['color']['white']}
    });
    logger?.d("Sending data: $data");
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
