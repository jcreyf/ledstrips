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
// Used to dynamically restart the app:
//   https://pub.dev/packages/flutter_phoenix
//   /> flutter pub add flutter_phoenix
import 'package:flutter_phoenix/flutter_phoenix.dart';
// Used to 'find' widgets dynamically:
//   https://docs.flutter.dev/cookbook/testing/widget/finders
import 'package:flutter_test/flutter_test.dart';

Future main() async {
  // Start the app:
  runApp(
    // Wrapping the app in a Phoenix widget that we can use to hot restart when needed.
    // (the Phoenix widget basically generates a new 'key' on itself, invalidating the
    // UI and regenerating everything)
    Phoenix(child:
      LedstripApp(),
    )
  );
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
  final title = "Ledstrips";
  static late LedstripApp me;

  LedstripApp() {
    super.key;
  }

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
  List<String> tabNames = [];
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
              addLedstrip(tabName: setting.key, endpoint: setting.value);
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

  void addLedstrip({required String tabName, required String endpoint}) {
    logger.i("Setting up ledstrip: $tabName -> $endpoint");
    Ledstrip? strip = Ledstrip();
    strip?.setLogger(logger);
    strip?.endpoint = endpoint;
    strip?.getMetadata(callback: (errors) => updatePage(errors));
    ledstrips.add(strip);
    tabNames.add(tabName);
  }

  // Method used as callback to async update the UI when new data comes in:
  void updatePage(String errors) {
    setState(() {
      if (errors != "") {
        // We got errors back from the API call!!!
        // This should be handled in the LedstripWidget.
        logger?.i("We got damn errors! $errors");
      }
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
      strip?.getMetadata(callback: (errors) => updatePage(errors));
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
    // The theme is set all the way in the beginning of the app.  Restart the app:
    Phoenix.rebirth(context);
  }

  void menuEditLedstrip() {
    int index = tabController.index;
    statusText = "Edit $index";
    editLedstrip(tabName: tabNames[index],
      endpoint: ledstrips[index]?.endpoint ?? "NA",
      callback: ((newTabName, newEndpoint) {
        setState(() {
          logger.i("Got: $newTabName, url: $newEndpoint");
          String oldTabName = tabNames[index];
          tabNames[index] = newTabName;
          settingsDatabase.update(type: "ledstrip", key: oldTabName, newKey: newTabName, value: newEndpoint);
          ledstrips[index]?.endpoint = newEndpoint;
          ledstrips[index]?.getMetadata(callback: (errors) => updatePage(errors));
        });
      })
    );
  }

  void menuAddLedstrip() {
    editLedstrip(tabName: "new",
        endpoint: "http://192.168.5.",
        callback: ((newTabName, newEndpoint) {
          setState(() {
            statusText = "Adding ledstrip: $newTabName, url: $newEndpoint";
            addLedstrip(tabName: newTabName, endpoint: newEndpoint);
            settingsDatabase.create(type: "ledstrip", key: newTabName, value: newEndpoint);
          });
        })
    );
  }

  void menuDeleteLedstrip() {
    int index = tabController.index;
    String tabName = tabNames[index];
    statusText = "Delete ledstrip: $index (name: '$tabName')";
    setState(() {
      // Delete the selected tab and move the focus to the previous tab.
      // Also remove the ledstrip from the backend database.
      ledstrips.removeAt(index);
      tabNames.removeAt(index);
      // Set the new tab index (keep at 0 if we're deleting the first tab):
      tabController.index = (index == 0 ? 0 : index - 1);
      settingsDatabase.delete(type: "ledstrip", key: tabName);
    });
  }

  void editLedstrip({required String tabName, required String endpoint, required Function callback}) {
    final nameController = TextEditingController(text: tabName);
    final urlController = TextEditingController(text: endpoint);

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Ledstrip'),
          content: SingleChildScrollView(
              child: ListBody(
                children: <Widget>[
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
                callback(nameController.text, urlController.text);
                Navigator.of(context).pop();
              },
            ),
          ],
        );
      }
    );
  }

  @override
  Widget build(BuildContext context) {
    // Show a spinner in the body unless if we have ledstrip data:
    Widget stripUI =  LoadingAnimationWidget.inkDrop(color: Colors.green, size: 60,);
    // We need our own custom tab controller to keep track of which tab is active:
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
                  for (var stripName in tabNames)
                    Tab(text: stripName,)
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
  }
}
