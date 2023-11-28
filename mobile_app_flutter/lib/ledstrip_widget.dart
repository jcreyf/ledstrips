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
  Widget build(BuildContext context) {
    widget.logger?.i(widget.ledstrip);
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        Text(
          widget.ledstrip?.name() ?? "None!",
          style: Theme.of(context).textTheme.displayLarge,
        ),
        HueRingPicker(
          pickerColor: widget.ledstrip?.getColor() ?? const Color.fromRGBO(0, 0, 0, 1.0),
          enableAlpha: false,
          displayThumbColor: true,
          onColorChanged: (Color color) {
            setState(() {
              widget.ledstrip?.setColor(color);
            });
          },
        ),
        Padding(
          padding: const EdgeInsets.all(50.0),
          child: Row(
              children: [
                Text(
                  'Brightness:',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                Slider(
                    value: widget.ledstrip?.getBrightness().toDouble() ?? 0.0,
                    max: 255,
                    divisions: 255,
                    label: widget.ledstrip?.getBrightness().round().toString(),
                    onChanged: (double value) {
                      setState(() {
                        widget.ledstrip?.setBrightness(value.toInt());
                      });
                    }),
                Material(
                  color: Colors.white,
                  child: Center(
                    child: Ink(
                      decoration: const ShapeDecoration(
                        color: Colors.green,
                        shape: CircleBorder(),
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
                                widget.ledstrip?.getMetadata(callback: () => setState(() => {}));
                              });
                        },
                        icon: const Icon(Icons.save),
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        Padding(
        padding: const EdgeInsets.all(10.0),
        child: Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              Switch(
                value: widget.ledstrip?.isOn() ?? false,
                activeColor: Colors.green,
                onChanged: (bool flag) {
                  setState(() {
                    // Toggle the ledstrip on/off:
                    widget.ledstrip?.updateMetadata(
                      toggle: true,
                      callback: () {
                        // the API call finished and is now executing this callback function.
                        // Here we trigger the Ledstrip API call asynchronously to get refreshed metadata
                        // ...and its callback function will update the data in the UI.
                        widget.ledstrip?.getMetadata(callback: () => setState(() => {}));
                      });
                  });
                },
              ),
            ],
          ),
        ),
      ],
    );
  }
}
