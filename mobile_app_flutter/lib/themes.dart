import 'package:flutter/material.dart';
// flutter add pub hexcolor
import 'package:hexcolor/hexcolor.dart';

class LedstripThemeClass {
  // https://flutter-theme-editor.rob-b.co.uk/#/
//  Color lightPrimaryColor = HexColor('#DF0054');
//  Color darkPrimaryColor = HexColor('#480032');
//  Color secondaryColor = HexColor('#FF8B6A');
//  Color accentColor = HexColor('#FFD2BB');
  Color lightPrimaryColor = const Color.fromRGBO(128, 128, 128, 1.0);
  Color darkPrimaryColor = const Color.fromRGBO(32, 32, 32, 1.0);
  Color secondaryColor = const Color.fromRGBO(128, 255, 128, 1.0);
  Color accentColor = const Color.fromRGBO(128, 128, 255, 1.0);

  static ThemeData lightTheme = ThemeData(
    brightness: Brightness.light,
    visualDensity: VisualDensity.standard,
    primarySwatch: Colors.blue,
//    accentColor: Colors.purpleAccent,
//    brightness: Brightness.light,
//    primaryColor: ThemeData.light().scaffoldBackgroundColor,
    primaryColor: Colors.green,
//    colorScheme: const ColorScheme.light().copyWith(
//      primary: _ledstripThemeClass.lightPrimaryColor,
//      secondary: _ledstripThemeClass.secondaryColor
//      ),
  );
  static ThemeData darkTheme = ThemeData(
    brightness: Brightness.dark,
    visualDensity: VisualDensity.standard,
    primarySwatch: Colors.red,
//    accentColor: Colors.purpleAccent,
//    brightness: Brightness.dark,
//    primaryColor: ThemeData.dark().scaffoldBackgroundColor,
    primaryColor: Colors.red,
//    colorScheme: const ColorScheme.dark().copyWith(
//      primary: _ledstripThemeClass.darkPrimaryColor,
//      secondary: _ledstripThemeClass.secondaryColor,
//    ),
//    floatingActionButtonTheme: const FloatingActionButtonThemeData(backgroundColor: Colors.yellow),
  );
}

LedstripThemeClass _ledstripThemeClass = LedstripThemeClass();