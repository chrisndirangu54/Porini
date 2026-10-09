import 'dart:convert';
import 'package:http/http.dart' as http;
import 'offline_store.dart';
class RangerSync {
 final OfflineStore store;final String baseUrl;final String apiKey;
 RangerSync(this.store,this.baseUrl,this.apiKey);
 Future<List<dynamic>> sync() async {
   final headers={'X-API-Key':apiKey,'Content-Type':'application/json'};
   for(final pending in await store.pending()){
     final response=await http.patch(Uri.parse('$baseUrl/incidents/${pending['incident_id']}/status'),
       headers:headers,body:jsonEncode({'status':pending['status']})).timeout(const Duration(seconds:10));
     if(response.statusCode!=200)throw StateError('Sync failed ${response.statusCode}');
     await store.markSynced(pending['id'] as int);
   }
   final response=await http.get(Uri.parse('$baseUrl/incidents'),headers:headers).timeout(const Duration(seconds:12));
   if(response.statusCode!=200)throw StateError('Fetch failed ${response.statusCode}');
   final data=jsonDecode(response.body) as List<dynamic>;
   await store.cacheIncidents(data);return data;
 }
}
