import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
void main()=>runApp(const PoriniApp());
class PoriniApp extends StatelessWidget{
 const PoriniApp({super.key});
 @override Widget build(BuildContext context)=>MaterialApp(title:'Porini Ranger',theme:ThemeData.dark(useMaterial3:true).copyWith(colorScheme:ColorScheme.fromSeed(seedColor:const Color(0xff60bd86),brightness:Brightness.dark)),home:const RangerHome());
}
class RangerHome extends StatefulWidget{const RangerHome({super.key});@override State<RangerHome> createState()=>_RangerHomeState();}
class _RangerHomeState extends State<RangerHome>{
 final server=TextEditingController(text:'http://10.0.2.2:8000');
 final key=TextEditingController();
 List<dynamic> incidents=[];String error='';bool loading=false;
 Future<void> refresh()async{
 setState((){loading=true;error='';});
 try{final r=await http.get(Uri.parse('${server.text}/incidents'),headers:{'X-API-Key':key.text}).timeout(const Duration(seconds:12));
 if(r.statusCode!=200)throw Exception('HTTP ${r.statusCode}');
 setState(()=>incidents=jsonDecode(r.body) as List<dynamic>);
 }catch(e){setState(()=>error=e.toString());}
 finally{setState(()=>loading=false);}
 }
 Future<void> acknowledge(String id)async{
 final r=await http.patch(Uri.parse('${server.text}/incidents/$id/status'),headers:{'X-API-Key':key.text,'Content-Type':'application/json'},body:jsonEncode({'status':'acknowledged'}));
 if(r.statusCode!=200){setState(()=>error='Acknowledgement failed: ${r.statusCode}');return;}await refresh();
 }
 @override Widget build(BuildContext context)=>Scaffold(appBar:AppBar(title:const Text('PORINI • Ranger Operations')),body:Padding(padding:const EdgeInsets.all(16),child:Column(children:[
 TextField(controller:server,decoration:const InputDecoration(labelText:'API URL')),
 TextField(controller:key,obscureText:true,decoration:const InputDecoration(labelText:'Authorized ranger API key')),
 const SizedBox(height:12),FilledButton.icon(onPressed:loading?null:refresh,icon:const Icon(Icons.refresh),label:const Text('Sync incidents')),
 if(error.isNotEmpty)Text(error,style:const TextStyle(color:Colors.orangeAccent)),
 const SizedBox(height:12),
 Expanded(child:ListView.builder(itemCount:incidents.length,itemBuilder:(context,index){
 final i=incidents[index] as Map<String,dynamic>;
 return Card(child:ListTile(title:Text('${i['priority']} • ${i['event_type']}'),
 subtitle:Text('${i['status']} • ${i['synthetic'] == true ? 'SYNTHETIC' : 'FIELD'} • ${i['latitude']}, ${i['longitude']}'),
 trailing:i['status']=='open'?TextButton(onPressed:()=>acknowledge(i['id'] as String),child:const Text('Acknowledge')):const Icon(Icons.check_circle_outline)));
 })),const Text('Prototype: online connection required; no offline queue or SOS dispatch.',style:TextStyle(fontSize:11))
 ])));}
}
