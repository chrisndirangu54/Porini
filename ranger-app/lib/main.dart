import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'offline_store.dart';
import 'sync_service.dart';
void main()=>runApp(const PoriniApp());
class PoriniApp extends StatelessWidget{
 const PoriniApp({super.key});
 @override Widget build(BuildContext context)=>MaterialApp(title:'Porini Ranger',theme:ThemeData.dark(useMaterial3:true).copyWith(colorScheme:ColorScheme.fromSeed(seedColor:const Color(0xff60bd86),brightness:Brightness.dark)),home:const RangerHome());
}
class RangerHome extends StatefulWidget{const RangerHome({super.key});@override State<RangerHome> createState()=>_RangerHomeState();}
class _RangerHomeState extends State<RangerHome>{
 final server=TextEditingController(text:'http://10.0.2.2:8000');
 final key=TextEditingController();
 List<dynamic> incidents=[];String error='';bool loading=false;OfflineStore? cache;
 final secret=TextEditingController();
 Future<void> showCached()async {try{cache ??=OfflineStore(secret.text); final items=await cache!.cachedIncidents();setState(()=>incidents=items);}catch(e){setState(()=>error='Offline data unavailable: $e');}}
 Future<void> refresh()async{
 setState((){loading=true;error='';});
 try{cache ??=OfflineStore(secret.text);final items=await RangerSync(cache!,server.text,key.text).sync();setState(()=>incidents=items);
 }catch(e){setState(()=>error='Network sync failed; showing encrypted cached incidents: $e');await showCached();}
 finally{setState(()=>loading=false);}
 }
 Future<void> acknowledge(String id)async{
 try{cache ??=OfflineStore(secret.text);await cache!.enqueueStatus(id,'acknowledged');setState(()=>incidents=incidents.map((e){if(e['id']==id)return {...e,'status':'acknowledged'};return e;}).toList());await refresh();}catch(e){setState(()=>error='Unable to queue acknowledgement: $e');}
 }
 @override Widget build(BuildContext context)=>Scaffold(appBar:AppBar(title:const Text('PORINI • Ranger Operations')),body:Padding(padding:const EdgeInsets.all(16),child:Column(children:[
 TextField(controller:server,decoration:const InputDecoration(labelText:'API URL')),
 TextField(controller:key,obscureText:true,decoration:const InputDecoration(labelText:'Authorized ranger API key')),
 TextField(controller:secret,obscureText:true,decoration:const InputDecoration(labelText:'Offline database encryption passphrase')),
 TextButton(onPressed:showCached,child:const Text('Open cached incidents (offline)')),
 const SizedBox(height:12),FilledButton.icon(onPressed:loading?null:refresh,icon:const Icon(Icons.refresh),label:const Text('Sync incidents')),
 if(error.isNotEmpty)Text(error,style:const TextStyle(color:Colors.orangeAccent)),
 const SizedBox(height:12),
 Expanded(child:ListView.builder(itemCount:incidents.length,itemBuilder:(context,index){
 final i=incidents[index] as Map<String,dynamic>;
 return Card(child:ListTile(title:Text('${i['priority']} • ${i['event_type']}'),
 subtitle:Text('${i['status']} • ${i['synthetic'] == true ? 'SYNTHETIC' : 'FIELD'} • ${i['latitude']}, ${i['longitude']}'),
 trailing:i['status']=='open'?TextButton(onPressed:()=>acknowledge(i['id'] as String),child:const Text('Acknowledge')):const Icon(Icons.check_circle_outline)));
 })),const Text('Encrypted cached incidents and queued acknowledgements are available offline. No offline maps or SOS dispatch.',style:TextStyle(fontSize:11))
 ])));}
}
