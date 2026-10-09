import 'dart:convert';
import 'package:sqflite_sqlcipher/sqflite.dart' as sql;
import 'package:path/path.dart' as path;
class OfflineStore {
 final String passphrase;
 sql.Database? _db;
 OfflineStore(this.passphrase);
 Future<sql.Database> open() async {
  if(passphrase.isEmpty)throw StateError('Non-empty encryption key required');
  if(_db!=null)return _db!;
  final root=await sql.getDatabasesPath();
  final db=await sql.openDatabase(path.join(root,'porini_ranger.db'),password:passphrase,version:1,onCreate:(database,version) async {
   await database.execute('CREATE TABLE incidents(id TEXT PRIMARY KEY, body TEXT NOT NULL)');
   await database.execute('CREATE TABLE outbox(id INTEGER PRIMARY KEY AUTOINCREMENT, incident_id TEXT NOT NULL, status TEXT NOT NULL)');
  });_db=db;return db;
 }
 Future<void> cacheIncidents(List<dynamic> items) async{
  final db=await open();final batch=db.batch();
  for(final obj in items){final entry=obj as Map<String,dynamic>;batch.insert('incidents',{'id':entry['id'],'body':jsonEncode(entry)},conflictAlgorithm:sql.ConflictAlgorithm.replace);}
  await batch.commit(noResult:true);
 }
 Future<List<dynamic>> cachedIncidents() async{
  final db=await open();return (await db.query('incidents')).map((x)=>jsonDecode(x['body'] as String)).toList();
 }
 Future<void> enqueueStatus(String id,String status) async{
  final db=await open();await db.insert('outbox',{'incident_id':id,'status':status});
 }
 Future<List<Map<String,dynamic>>> pending() async=>(await (await open()).query('outbox',orderBy:'id ASC'));
 Future<void> markSynced(int id) async=>(await (await open()).delete('outbox',where:'id=?',whereArgs:[id]));
}
