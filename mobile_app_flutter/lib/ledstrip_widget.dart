import 'package:mobile_app_flutter/ledstrip.dart';
import 'package:flutter/material.dart';
// https://pub.dev/packages/logger
import 'package:logger/logger.dart';
// https://pub.dev/packages/flutter_colorpicker
// /> flutter pub add flutter_colorpicker
import 'package:flutter_colorpicker/flutter_colorpicker.dart';

class LedstripWidget extends StatefulWidget {
  final Ledstrip? ledstrip;
  final Logger? logger;

  const LedstripWidget({
    Key? key,
    this.ledstrip,
    this.logger,
  }) : super(key: key);

  @override
  _LedstripWidgetState createState() => _LedstripWidgetState();
}

class _LedstripWidgetState extends State<LedstripWidget> {
  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    Widget page;
    if (widget.ledstrip?.hasErrors ?? false) {
      page = Container(
        color: Colors.red.shade900,
        child: Padding(
          padding: const EdgeInsets.all(10.0),
          child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                Text(widget.ledstrip?.errors ?? "No idea what's going on",
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.yellowAccent,
                    fontSize: 35,
                  ),
                ),
                Text(widget.ledstrip?.endpoint ?? "The ledstrip has no endpoint set!",
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.white,
                    fontSize: 20,
                  ),
                ),
              ],
          )
        ),
      );
    } else {
      Widget colorPicker;
      if(widget.ledstrip?.behaviorName == "Default") {
        colorPicker = HueRingPicker(
          // https://github.com/mchome/flutter_colorpicker/blob/master/example/lib/main.dart
          pickerColor: widget.ledstrip?.color ??
              const Color.fromRGBO(0, 0, 0, 1.0),
          enableAlpha: false,
          displayThumbColor: true,
          onColorChanged: (Color color) {
            setState(() {
              widget.ledstrip?.color = color;
            });
          },
        );
      } else {
        // Blank out the same height of the HueRingPicker:
        colorPicker = const SizedBox(height: 370,);
      }
      page = RefreshIndicator(
        onRefresh: () async {
          // The page got pulled down.  We need to fetch new data:
          widget.ledstrip?.getMetadata(callback: () => setState(() => {}));
          // The child of a RefreshIndicator needs to be a scrollable widget!
          // Our app is not "scrollable" but we can force it by putting everything
          // in a SingleChildScrollView and setting its 'physics' to 'AlwaysScrollableScrollPhysics'.
          // Also, its child widget needs to have the height of the screen!
        },
        child: SingleChildScrollView(
          padding: const EdgeInsets.only(top: 20.0),
          physics: const AlwaysScrollableScrollPhysics(),
          child: Container(
            // Only the ledstip widget part of the screen can get pulled down for refresh.
            // We need to limit the size to: screen height - app bar height - status bar header height
            // Since the app bar is part of the scaffold, we can query its height through the scaffold:
            height: MediaQuery.of(context).size.height ?? 0.0 - (Scaffold.of(context).appBarMaxHeight ?? 0.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.start,
              children: <Widget>[
                Text(
                  widget.ledstrip?.name ?? "None!",
                  style: Theme.of(context).textTheme.displayLarge,
                ),
                const SizedBox(height: 10,),
                DropdownMenu<String>(
                  label: const Text('Behavior'),
                  initialSelection: Ledstrip.behaviorNames.first,
                  dropdownMenuEntries: Ledstrip.behaviorNames.map<DropdownMenuEntry<String>>((String value) {
                      return DropdownMenuEntry<String>(value: value, label: value);
                    }).toList(),
                  onSelected: (String? value) {
                    // This is called when the user selects an item.
                    setState(() {
                      widget.ledstrip?.behaviorName = value!;
                      // Update the ledstrip configuration:
                      widget.ledstrip?.updateMetadata(
                          toggle: false,
                          callback: () {
                            // the API call finished and is now executing this callback function.
                            // Here we trigger the Ledstrip API call asynchronously to get refreshed metadata
                            // ...and its callback function will update the data in the UI.
                            widget.ledstrip?.getMetadata(
                              // Ignoring errors and proving an empty callback method:
                              callback: ((errors) {})
                            );
                          }
                        );
                    });
                  },
                ),
                const SizedBox(height: 10,),
                colorPicker,
                const SizedBox(height: 10,),
                Padding(
                  padding: const EdgeInsets.fromLTRB(30, 0, 30, 0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Brightness:',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      SliderTheme(
                        data: SliderTheme.of(context).copyWith(
                          activeTrackColor: Colors.blue,
                          inactiveTrackColor: Colors.blue,
                          trackShape: const RectangularSliderTrackShape(),
                          trackHeight: 5.0,
                          thumbColor: Colors.green,
                          thumbShape: const RoundSliderThumbShape(
                              enabledThumbRadius: 15.0),
                          overlayColor: Colors.red.withAlpha(32),
                          overlayShape: const RoundSliderOverlayShape(
                              overlayRadius: 20.0),
                          //                    overlayShape: SliderComponentShape.noOverlay,
                        ),
                        child: Slider(
                          value: widget.ledstrip?.brightness.toDouble() ?? 0.0,
                          min: 1,
                          max: 255,
                          divisions: 255,
                          label: widget.ledstrip?.brightness.round().toString(),
                          onChanged: (double value) {
                            setState(() {
                              widget.ledstrip?.brightness = value.toInt();
                            });
                          }),
                      ),
                      Material(
                        color: Colors.white,
                        child: Center(
                          child: Ink(
                            decoration: const ShapeDecoration(
                              color: Colors.green,
                              shape: CircleBorder(
                                  side: BorderSide(
                                    color: Colors.orange,
                                    width: 2.0,
                                  )
                              ),
                            ),
                            child: IconButton(
                              onPressed: () {
                                // Update the ledstrip configuration:
                                widget.ledstrip?.updateMetadata(
                                    toggle: false,
                                    callback: () {
                                      // the API call finished and is now executing this callback function.
                                      // Here we trigger the Ledstrip API call asynchronously to get refreshed metadata
                                      // ...and its callback function will update the data in the UI.
                                      widget.ledstrip?.getMetadata(
                                          callback: () => setState(() => {}));
                                    });
                              },
                              icon: const Icon(Icons.save),
                              color: Colors.white,
                              //                            color: MediaQuery.of(context).platformBrightness == Brightness.light ? Colors.white : Colors.black,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 10,),
                Padding(
                  padding: const EdgeInsets.fromLTRB(10, 0, 10, 0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      ElevatedButton(
                          onPressed: () {
                            setState(() {
                              widget.ledstrip?.reset();
                            });
                          },
                          child: const Text('Reset Colors')
                      ),
                      Switch(
                        value: widget.ledstrip?.isOn() ?? false,
                        activeColor: Colors.green,
                        onChanged: (bool flag) {
                          // Toggle the ledstrip on/off:
                          widget.ledstrip?.updateMetadata(
                              toggle: true,
                              callback: () {
                                // the API call finished and is now executing this callback function.
                                // Here we trigger the Ledstrip API call asynchronously to get refreshed metadata
                                // ...and its callback function will update the data in the UI.
                                widget.ledstrip?.getMetadata(
                                    callback: () => setState(() => {}));
                              }
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return page;
  }
}
