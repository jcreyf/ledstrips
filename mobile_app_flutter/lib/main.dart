/*
  Classes:  https://api.flutter.dev/flutter/widgets/AbsorbPointer-class.html
  Cookbook: https://docs.flutter.dev/cookbook/networking/send-data
  Material: https://api.flutter.dev/flutter/material/Scaffold-class.html

  flutter build apk --release

  ToDo:
  - change app icon;
  - change app splashscreen;
 */
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:mobile_app_flutter/themes.dart';
// Ledstrip stuff:
import 'package:mobile_app_flutter/ledstrip.dart';
import 'package:mobile_app_flutter/ledstrip_widget.dart';
import 'package:mobile_app_flutter/ledstrip_settings.dart';
// Logging stuff:
//   https://pub.dev/packages/logger
import 'package:logger/logger.dart';
// Wait spinner stuff:
//   https://pub.dev/packages/loading_animation_widget
//   /> flutter pub add loading_animation_widget
import 'package:loading_animation_widget/loading_animation_widget.dart';
// Used to 'find' widgets dynamically:
//   https://docs.flutter.dev/cookbook/testing/widget/finders
import 'package:flutter_test/flutter_test.dart';

Future main() async {
  // Start the app:
  runApp(LedstripApp());
}

//-------------

class Menu {
  static const String Theme = 'Theme';
  static const String EditLedstrip = 'Edit Ledstrip';
  static const String AddLedstrip = 'Add Ledstrip';
  static const String DeleteLedstrip = 'Delete Ledstrip';
  static const List<String> menuItems = <String>[Theme, EditLedstrip, AddLedstrip, DeleteLedstrip];
}

//-------------

class LedstripApp extends StatelessWidget {
  LedstripApp({super.key});
  final title = "Ledstrips";

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: title,
      home: LedstripsHomePage(title: title),
      themeMode: LedstripSetting.systemTheme ? ThemeMode.system : (LedstripSetting.darkTheme ? ThemeMode.dark : ThemeMode.light),
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

//-------------

// The App's UI
// We need to implement from 'SingleTickerProviderStateMixin' so that this class can be
// used as 'vsync' object in the TabController:
class _LedstripsHomePageState extends State<LedstripsHomePage> with TickerProviderStateMixin {
  final Logger logger = Logger();
  final settingsDatabase = SettingsDatabase();
  late TabController tabController;
  List<Ledstrip?> ledstrips = [];
  int currentTab = 0;
  String statusText = "";

  @override
  void initState() {
    super.initState();
    // This is just for debugging and should be removed at some point:
    createSettings();
    loadSettings();
  }

  @override
  void dispose() {
    tabController.dispose();
    super.dispose();
  }

  void onTabChange() {
    if (!tabController.indexIsChanging) {
      currentTab = tabController.index;
    }
  }

  void createSettings() async {
    // Create a sqlite database if not there yet and store these settings (if not there yet):
    await settingsDatabase.create(type: "setting", key: "theme", value: "dark");
    await settingsDatabase.create(type: "setting", key: "default_tab", value: "Luna");
    await settingsDatabase.create(type: "ledstrip", key: "loft", value: "http://192.168.5.11:8888/light/Loft");
    await settingsDatabase.create(type: "ledstrip", key: "luna", value: "http://192.168.5.12:8888/light/Luna");
  }

  void loadSettings() {
    setState(() {
      settingsDatabase.fetchAll().then((settings) {
        for (var setting in settings) {
          switch(setting.type) {
            // Process app settings:
            case "setting":
              logger.i("Setting: $setting");
              switch(setting.key) {
                // Process display theme setting:
                case "theme":
                  setTheme(themeName: setting.value);
                  break;
                // Process default tab setting:
                case "default_tab":
                  LedstripSetting.defaultTab = setting.value;
                  statusText+="\nSelect tab: ${LedstripSetting.defaultTab}";
                  break;
              }
              break;
            // Process ledstrip settings:
            case "ledstrip":
              addLedstrip(name: setting.key, endpoint: setting.value);
              break;
          }
        }
      });
    });
  }

  void setTheme({required String themeName}) {
    switch(themeName) {
      case "system":
        LedstripSetting.systemTheme = true;
        LedstripSetting.darkTheme = false;
        statusText="Theme: system";
        break;
      case "dark":
        LedstripSetting.systemTheme = false;
        LedstripSetting.darkTheme = true;
        statusText="Theme: dark";
        break;
      case "light":
        LedstripSetting.systemTheme = false;
        LedstripSetting.darkTheme = false;
        statusText="Theme: light";
        break;
    }
  }

  void addLedstrip({required String name, required String endpoint}) {
    logger.i("Setting up ledstrip: $name -> $endpoint");
    Ledstrip? strip = Ledstrip();
    strip?.setLogger(logger);
    strip?.endpoint = endpoint;
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
    statusText = "Toggle ledstrip ${strip?.name} $flag";
    // Run the Ledstrip API call asynchronously to toggle the strip:
    strip?.updateMetadata(callback: () {
      // the API call finished and is now executing this callback function.
      // Here we trigger the Ledstrip API call asynchronously to get refreshed metadata
      // ...and its callback function will update the data in the UI.
      strip?.getMetadata(callback: () => updatePage());
    });
  }

  void menuAction(String menuItem) {
    setState(() {
      switch(menuItem) {
        case(Menu.Theme):
          menuTheme();
          break;
        case(Menu.EditLedstrip):
          menuEditLedstrip();
          break;
        case(Menu.AddLedstrip):
          menuAddLedstrip();
          break;
        case(Menu.DeleteLedstrip):
          menuDeleteLedstrip();
          break;
      }
    });
  }

  void menuTheme() {
    // Toggle through the themes:
    String theme;
    if (LedstripSetting.systemTheme) {
      LedstripSetting.systemTheme = false;
      LedstripSetting.darkTheme = true;
      theme="dark";
    } else if (LedstripSetting.darkTheme) {
      LedstripSetting.systemTheme = false;
      LedstripSetting.darkTheme = false;
      theme="light";
    } else {
      LedstripSetting.systemTheme = true;
      LedstripSetting.darkTheme = false;
      theme="system";
    }
    statusText = "Switching to $theme theme";
    settingsDatabase.update(type: "setting", key: "theme", value: theme);
  }

  void menuEditLedstrip() {
    int index = tabController.index;
    statusText = "Edit $index";
    var (newName, newEndpoint) = editLedstrip(name: ledstrips[index]?.name, endpoint: ledstrips[index]?.endpoint);
    logger.i("Update ledstrip: $newName (url: $newEndpoint)");
  }

  void menuAddLedstrip() {
    var (newName, newEndpoint) = editLedstrip(name: "new", endpoint: "http://");
    logger.i("Creating new ledstrip: $newName (url: $newEndpoint)");
//    addLedstrip(name: newName, endpoint: newEndpoint);
//    settingsDatabase.create(type: "ledstrip", key: newName, value: newEndpoint);
  }

  void menuDeleteLedstrip() {
    int index = tabController.index;
    String ledstripName = ledstrips[index]?.name ?? "NA";
    statusText = "Delete ledstrip: $index (name: '$ledstripName')";
    setState(() {
      // Delete the selected tab and move the focus to the previous tab.
      // Also remove the ledstrip from the backend database.
      ledstrips.removeAt(index);
      tabController.index = index - 1;
      settingsDatabase.delete(type: "ledstrip", key: ledstripName);
    });
  }

  (String, String) editLedstrip({required String? name, required String? endpoint}) {
    String newName = name ?? "";
    String newEndpoint = endpoint ?? "";
    final nameController = TextEditingController(text: newName);
    final urlController = TextEditingController(text: newEndpoint);

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
            title: const Text('Ledstrip'),
            content: SingleChildScrollView(
              child: ListBody(
                children: <Widget>[
                  Text(
                    'Ledstrip details',
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                  Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Name:'),
                        SizedBox(
                          width: 100,
                          child: TextField(
                            controller: nameController,
                          ),
                        ),
                      ],
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('API endpoint:'),
                      SizedBox(
                        width: 150,
                        child: TextField(
                          controller: urlController,
                        ),
                      ),
                    ],
                  ),
                ],
              )
            ),
            actions: [
              TextButton(
                child: const Text('Cancel'),
                onPressed: () {
                  Navigator.of(context).pop();
                },
              ),
              TextButton(
                child: const Text('Save'),
                onPressed: () {
                  newName = nameController.text;
                  newEndpoint = urlController.text;
                  logger.i("Name: $newName (url: $newEndpoint)");
                  Navigator.of(context).pop();
                },
              ),
            ],
          );
      },
    );
    return (newName, newEndpoint);
  }

  @override
  Widget build(BuildContext context) {
    // Show a spinner in the body unless if we have ledstrip data:
    Widget stripUI =  LoadingAnimationWidget.inkDrop(color: Colors.green, size: 60,);
    tabController = TabController(length: ledstrips.length, vsync: this, initialIndex: currentTab);
    tabController.addListener(onTabChange);
    // Now generate the full UI:
    return Scaffold(
          appBar: AppBar(
            title: Text(widget.title),
            foregroundColor: Colors.yellow,
            backgroundColor: Theme.of(context).colorScheme.inversePrimary,
            bottom: TabBar(
                controller: tabController,
                indicatorSize: TabBarIndicatorSize.tab,
                indicator: BoxDecoration(
                  borderRadius: BorderRadius.circular(5),
                  gradient: const LinearGradient(
                    colors: [Colors.deepPurple, Colors.deepPurpleAccent],
                  ),
                ),
                unselectedLabelColor: Colors.grey,
                tabs: <Widget>[
                  for (var strip in ledstrips)
                    Tab(text: strip?.name,)
                ],
            ),
            actions: <Widget>[
              IconButton(
                  icon: Icon(Icons.lightbulb),
                  onPressed: () {
                    setState(() {
                      statusText = "clicked lightbulb";
                    });
                  }
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
            controller: tabController,
            children: <Widget>[
              for (var strip in ledstrips)
                LedstripWidget(ledstrip: strip, logger: logger,)
            ]
          ),
          bottomNavigationBar: Container(
            color: Theme.of(context).colorScheme.inversePrimary,
            child: Text(statusText),
          ),
        );



    // return DefaultTabController(
    //   length: ledstrips.length,
    //   initialIndex: 1,
    //   child: Scaffold(
    //     appBar: AppBar(
    //       title: Text(widget.title),
    //       foregroundColor: Colors.yellow,
    //       backgroundColor: Theme.of(context).colorScheme.inversePrimary,
    //       bottom: TabBar(
    //         key: const Key('LedstripTabs'),
    //         indicatorSize: TabBarIndicatorSize.tab,
    //         indicator: BoxDecoration(
    //           borderRadius: BorderRadius.circular(5),
    //           gradient: const LinearGradient(
    //             colors: [Colors.deepPurple, Colors.deepPurpleAccent],
    //           ),
    //         ),
    //         unselectedLabelColor: Colors.grey,
    //         tabs: <Widget>[
    //           for (var strip in ledstrips)
    //             Tab(text: strip?.name() ?? 'N/A'),
    //         ]
    //       ),
    //       actions: <Widget>[
    //         IconButton(
    //           icon: Icon(Icons.lightbulb),
    //           onPressed: () {
    //             setState(() {
    //               statusText = "clicked lightbulb";
    //             });
    //           }
    //         ),
    //        PopupMenuButton<String>(
    //           onSelected: menuAction,
    //           itemBuilder: (BuildContext context) {
    //             return Menu.menuItems.map((String menuItem) {
    //               return PopupMenuItem<String>(
    //                 value: menuItem,
    //                 child: Row(
    //                   children: [
    //                     Text(menuItem),
    //                     Icon(Icons.edit),
    //                   ],
    //                 ),
    //               );
    //             }).toList();
    //           },
    //         )
    //       ],
    //     ),
    //     body: TabBarView(
    //       children: <Widget>[
    //         for (var strip in ledstrips)
    //             LedstripWidget(ledstrip: strip, logger: logger,)
    //       ]
    //     ),
    //     bottomNavigationBar: Container(
    //       color: Theme.of(context).colorScheme.inversePrimary,
    //       child: Text(statusText),
    //     ),
    //   )
    // );
  }
}
