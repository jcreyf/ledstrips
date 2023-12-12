/*
  Classes:  https://api.flutter.dev/flutter/widgets/AbsorbPointer-class.html
  Cookbook: https://docs.flutter.dev/cookbook/networking/send-data
  Material: https://api.flutter.dev/flutter/material/Scaffold-class.html

  flutter build apk --release
  mv build/app/outputs/flutter-apk/app-release.apk build/app/outputs/flutter-apk/ledstrips.apk

  ToDo:
  - change app icon;
  - change app splashscreen;
 */
import 'package:mobile_app_flutter/ledstrip.dart';
import 'package:mobile_app_flutter/ledstrip_widget.dart';
import 'package:mobile_app_flutter/themes.dart';

// https://pub.dev/packages/logger
import 'package:logger/logger.dart';
import 'package:flutter/material.dart';
//https://pub.dev/packages/loading_animation_widget
// flutter pub add loading_animation_widget
import 'package:loading_animation_widget/loading_animation_widget.dart';

void main() {
  runApp(const LedstripApp());
}

class LedstripSettings {
  static bool systemTheme = true;
  static bool darkTheme = true;
}
class Menu {
  static const String Theme= 'Theme';
  static const String Settings = 'Settings';
  static const String Sync = 'Synchronize';
  static const List<String> menuItems = <String>["Theme", "Settings", "Synchronize"];
}

class LedstripApp extends StatelessWidget {
  const LedstripApp({super.key});
  final title = "Ledstrips";

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: title,
      home: LedstripsHomePage(title: title),
      themeMode: LedstripSettings.systemTheme ? ThemeMode.system : (LedstripSettings.darkTheme ? ThemeMode.dark : ThemeMode.light),
      theme: LedstripThemeClass.lightTheme,
      darkTheme: LedstripThemeClass.darkTheme,
    );
  }
}

//-------------

class LedstripsHomePage extends StatefulWidget {
  const LedstripsHomePage({super.key, required this.title});
  final String title;

  @override
  State<LedstripsHomePage> createState() => _LedstripsHomePageState();
}

// The App's UI
class _LedstripsHomePageState extends State<LedstripsHomePage> {
  final Logger logger = Logger();
  List<Ledstrip?> ledstrips = [];

  // Constructor:
  _LedstripsHomePageState() {
    logger.i("setting up a ledstrip");
    Ledstrip? strip = Ledstrip();
    strip?.setLogger(logger);
    strip?.setEndpoint("http://192.168.5.11:8888/light/Loft");
    strip?.getMetadata(callback: () => updatePage());
    ledstrips.add(strip);

    strip = Ledstrip();
    strip?.setLogger(logger);
    strip?.setEndpoint("http://192.168.5.12:8888/light/Luna");
    strip?.getMetadata(callback: () => updatePage());
    ledstrips.add(strip);
  }

  // Method used as callback to async update the UI when new data comes in:
  void updatePage() {
    setState(() {
      logger?.d("refresh the page with new data...");
    });
  }

  // Method to turn the ledstrip on or off:
  void toggleLedstrip(bool flag) {
    Ledstrip? strip = ledstrips[DefaultTabController.of(context).index];
    logger.i("Toggle ledstrip ${strip?.name()} $flag");
    // Run the Ledstrip API call asynchronously to toggle the strip:
    strip?.updateMetadata(callback: () {
      // the API call finished and is now executing this callback function.
      // Here we trigger the Ledstrip API call asynchronously to get refreshed metadata
      // ...and its callback function will update the data in the UI.
      strip?.getMetadata(callback: () => updatePage());
    });
  }

  void menuAction(String menuItem) {
    if (menuItem == Menu.Settings) {
      print('Settings');
    }
    else if (menuItem == Menu.Theme) {
      print('Theme');
    }
    else if (menuItem == Menu.Sync) {
      print('Sync');
    }
  }

  @override
  Widget build(BuildContext context) {
    // Show a spinner in the body unless if we have ledstrip data:
    Widget stripUI =  LoadingAnimationWidget.inkDrop(color: Colors.green, size: 60,);

    // Use the ledstrip that is set up in the active tab.
    // There will be no tabs the very first time this code runs.  In that case,
    // take the 1st element in the ledstrips collection:
//     int tabNumber = 0;
//     if (context.findAncestorWidgetOfExactType<DefaultTabController>() != null) {
//       tabNumber = DefaultTabController.of(context).index;
//     }
//     Ledstrip? strip = ledstrips[tabNumber];
//
//     // Create the UI for the selected ledstrip (if it has valid data):
//     if (strip?.hasMetadata() ?? true) {
//       stripUI = LedstripWidget(ledstrip: strip, logger: logger,);
//     }
//     logger.i("${ledstrips.length} ledstrips");

    // Now generate the full UI:
    return DefaultTabController(
      length: ledstrips.length,
      child: Scaffold(
        appBar: AppBar(
          title: Text(widget.title),
          foregroundColor: Colors.yellow,
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          bottom: TabBar(
            tabs: <Widget>[
              for (var strip in ledstrips)
                Tab(text: strip?.name() ?? 'N/A'),
          ]),
          actions: <Widget>[
            IconButton(
              icon: Icon(Icons.lightbulb),
              onPressed: () {},
            ),
          IconButton(
            icon: Icon(Icons.search),
            onPressed: () {},
          ),
           PopupMenuButton<String>(
              onSelected: menuAction,
              itemBuilder: (BuildContext context) {
                return Menu.menuItems.map((String menuItem) {
                  return PopupMenuItem<String>(
                    value: menuItem,
                    child: Row(
                      children: [
                        Text(menuItem),
                        Icon(Icons.edit),
                      ],
                    ),
                  );
                }).toList();
              },
            )
          ],
        ),
        body: TabBarView(
          children: <Widget>[
            for (var strip in ledstrips)
                LedstripWidget(ledstrip: strip, logger: logger,)
          ]),
      )
    );
  }
}
