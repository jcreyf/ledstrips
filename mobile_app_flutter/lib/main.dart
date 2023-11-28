/*
  Classes:  https://api.flutter.dev/flutter/widgets/AbsorbPointer-class.html
  Cookbook: https://docs.flutter.dev/cookbook/networking/send-data
  Material: https://api.flutter.dev/flutter/material/Scaffold-class.html

  flutter build apk --release
 */
import 'package:mobile_app_flutter/ledstrip.dart';
import 'package:mobile_app_flutter/ledstrip_widget.dart';
// https://pub.dev/packages/logger
import 'package:logger/logger.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const LedstripApp());
}

class LedstripApp extends StatelessWidget {
  const LedstripApp({super.key});
  final title = "Ledstrips";

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: title,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.greenAccent),
        useMaterial3: true,
      ),
      home: MyHomePage(title: title),
    );
  }
}

//-------------

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});
  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

// The App's UI
class _MyHomePageState extends State<MyHomePage> {
  final Logger logger = Logger();
  Ledstrip? _loft;

  // Constructor:
  _MyHomePageState() {
    logger.i("setting up a ledstrip");
    _loft = Ledstrip();
    _loft?.setLogger(logger);
    _loft?.setEndpoint("http://192.168.5.11:8888/light/Loft");
    _loft?.getMetadata(callback: () => updatePage());
  }

  // Method used as callback to async update the UI when new data comes in:
  void updatePage() {
    setState(() {
      logger?.d("refresh the page with new data...");
    });
  }

  // Method to turn the ledstrip on or off:
  void toggleLedstrip(bool flag) {
    logger.i("Turn the ledstrip $flag");
    // Run the Ledstrip API call asynchronously to toggle the strip:
    _loft?.updateMetadata(callback: () {
      // the API call finished and is now executing this callback function.
      // Here we trigger the Ledstrip API call asynchronously to get refreshed metadata
      // ...and its callback function will update the data in the UI.
      _loft?.getMetadata(callback: () => updatePage());
    });
  }

  @override
  Widget build(BuildContext context) {
    // https://github.com/mchome/flutter_colorpicker/blob/master/example/lib/main.dart
    return DefaultTabController(
        length: 3,
        child: Scaffold(
          appBar: AppBar(
            title: Text(widget.title),
            foregroundColor: Colors.yellow,
            backgroundColor: Theme.of(context).colorScheme.inversePrimary,
            bottom: TabBar(
                tabs: const <Widget>[
                  Tab(text: 'Loft'),
                  Tab(text: 'Slaapkamer'),
                  Tab(text: 'Luna'),
                ]),
          ),
          body: TabBarView(
              children: <Widget>[
                LedstripWidget(
                  ledstrip: _loft,
                  logger: logger,
                ),
                Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: <Widget>[
                      Text(
                        'Slaapkamer',
                        style: Theme.of(context).textTheme.headlineMedium,
                      ),
                    ]),
                Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: <Widget>[
                      Text(
                        'Luna',
                        style: Theme.of(context).textTheme.headlineMedium,
                      ),
                    ]),
              ]),
        )
    );
  }
}
