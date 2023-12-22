// SQLLite stuff:
//   https://docs.flutter.dev/cookbook/persistence/sqlite
//   /> flutter pub add sqflite path
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:flutter/widgets.dart';

class LedstripSetting {
  final String type;
  final String key;
  final String value;
  final String createdAt;
  final String? updatedAt;

  static bool systemTheme = true;
  static bool darkTheme = false;
  static String defaultTab = "";

  LedstripSetting({
    required this.type,
    required this.key,
    required this.value,
    required this.createdAt,
    this.updatedAt,
  });

  factory LedstripSetting.fromSqfliteDatabase(Map<String, dynamic> map) => LedstripSetting(
    type: map['type'] ?? '',
    key: map['key'] ?? '',
    value: map['value'] ?? '',
    createdAt: DateTime.fromMicrosecondsSinceEpoch(map['created_at']).toIso8601String(),
    updatedAt: map['updated_at'] == null
        ? null
        : DateTime.fromMillisecondsSinceEpoch(map['updated_at']).toIso8601String(),
  );

  String toString() {
    return "Type: $type, key: $key, value: $value";
  }
}

//-------------

class DatabaseService {
  Database? _database;

  Future<String> get fullPath async {
    const name = 'ledstrips.db';
    final path = await getDatabasesPath();
    return join(path, name);
  }

  Future<Database> get database async {
    if (_database != null) {
      return _database!;
    }
    _database = await _initialize();
    return _database!;
  }

  Future<Database> _initialize() async {
    WidgetsFlutterBinding.ensureInitialized();
    final path = await fullPath;
    print("Open database: $path");
    // Relative path on my laptop:
    //   /.dart_tool/sqflite_common_ffi/databases/ledstrips.db
    var database = await openDatabase(
      path,
      version: 1,
      onCreate: create,
      singleInstance: true,
    );
    return database;
  }

  Future<void> create(Database database, int version) async =>
      await SettingsDatabase().createTable(database);
}

//-------------

class SettingsDatabase {
  final tableName = 'settings';

  Future<void> createTable(Database database) async {
    // https://www.sqlite.org/lang_createtable.html
    await database.execute("""CREATE TABLE IF NOT EXISTS $tableName (
      type TEXT NOT NULL,
      key TEXT NOT NULL,
      value TEXT NOT NULL,
      created_at INTEGER NOT NULL DEFAULT (CAST(strftime('%s', 'now') AS INTEGER)),
      updated_at INTEGER,
      PRIMARY KEY(type, key)
    );""");
  }

  /*
    Insert a record if it does not exist yet
   */
  Future<int> create({required String type, required String key, required String value}) async {
    final database = await DatabaseService().database;
    return await database.rawInsert(
      '''INSERT OR IGNORE INTO $tableName (type,key,value,created_at) VALUES (?,?,?,?)''',
      [type, key, value, DateTime.now().millisecondsSinceEpoch],
    );
  }

// ToDo: the next 2 methods can probably be rolled into 1 generic method:
  Future<List<LedstripSetting>> fetchAll() async {
    final database = await DatabaseService().database;
    final ledstripSettings = await database.rawQuery(
      '''SELECT * FROM $tableName ORDER BY type, key''',
    );
    return ledstripSettings.map((setting) => LedstripSetting.fromSqfliteDatabase(setting)).toList();
  }
  Future<List<LedstripSetting>> fetchByType(String type) async {
    final database = await DatabaseService().database;
    final ledstripSetting = await database.rawQuery(
        '''SELEcT * FROM $tableName WHERE type = ?''', [type]
    );
    return ledstripSetting.map((setting) => LedstripSetting.fromSqfliteDatabase(setting)).toList();
  }

  Future<LedstripSetting> fetchByTypeAndKey(String type, String key) async {
    final database = await DatabaseService().database;
    final ledstripSetting = await database.rawQuery(
      '''SELEcT * FROM $tableName WHERE type = ? AND key = ?''', [type, key]
    );
    return LedstripSetting.fromSqfliteDatabase(ledstripSetting.first);
  }

  Future<int> update({required String type, required String key, String newKey = "", required String value}) async {
    final database = await DatabaseService().database;
    if (newKey == "") newKey = key;
    return await database.update(
      tableName,
      {
        'type': type,
        'key': newKey,
        'value': value,
        'updated_at': DateTime.now().millisecondsSinceEpoch
      },
      where: 'type = ? AND key = ?',
      conflictAlgorithm: ConflictAlgorithm.rollback,
      whereArgs: [type, key],
    );
  }

  Future<void> delete({required String type, String key = "N/A"}) async {
    final database = await DatabaseService().database;
    if (key == "N/A") {
      await database.rawDelete(
          '''DELETE FROM $tableName WHERE type = ?''', [type]
      );
    } else {
      await database.rawDelete(
          '''DELETE FROM $tableName WHERE type = ? AND key = ?''', [type, key]
      );
    }
  }
}