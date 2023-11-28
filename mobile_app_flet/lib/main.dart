import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:serious_python/serious_python.dart';
//import 'package:flutter/material.dart';
import 'package:flet/flet.dart';
import 'package:path/path.dart' as path;

void main() async {
  var fletPlatform = "";
  var appContainer = "app/ledstrips.zip";
  var appEntry = "main.py";

  if (defaultTargetPlatform == TargetPlatform.iOS) {
    fletPlatform = "iOS";
  } else if (defaultTargetPlatform == TargetPlatform.android) {
    fletPlatform = "Android";
  }

//  SeriousPython.run(appContainer, appFileName: appEntry);

  // extract app from asset
  var appDir = await extractAssetZip(appContainer);

  // set current directory to app path
  Directory.current = appDir;
  SeriousPython.runProgram(path.join(appDir, appEntry),
      environmentVariables: {
        "FLET_PLATFORM": fletPlatform,
        "FLET_SERVER_UDS_PATH": "flet.sock"
      });
  runApp(FletApp(
    pageUrl: "flet.sock",
    assetsDir: path.join(appDir, "assets"),
  ));

}
