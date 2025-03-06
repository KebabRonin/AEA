/*********************************************
 * OPL 22.1.2.0 Model
 * Author: Sebi
 * Creation Date: Mar 5, 2025 at 7:37:31 PM
 *********************************************/

using CP;

 {string} Countries = {"Belgium", "Denmark", "France", "Germany", "Luxembourg", "Netherlands"};
 
 range r = 0..3;
 string Names[r] = ["blue", "white", "yellow", "green"];
 
dvar int Belgium in r; 
dvar int Denmark in r;
dvar int France in r;
dvar int Germany in r;
dvar int Luxembourg in r;
dvar int Netherlands in r;
dvar int Switzerland in r;


subject to {
  France != Belgium;
  France != Luxembourg;
  France != Germany;
  Belgium != Netherlands;
  Belgium != Luxembourg;
  Belgium != Germany;
  Luxembourg != Germany;
  Netherlands != Germany;
  Switzerland  != France;
  Switzerland != Germany;
  Germany == Denmark;
  
};

execute {
    writeln("Solution:");
    writeln("France:", Names[France]);
    writeln("Luxembourg:", Names[Luxembourg]);
    writeln("Belgium:", Names[Belgium]);
    writeln("Germany:", Names[Germany]);
    writeln("Netherlands:", Names[Netherlands]);
    writeln("Denmark:", Names[Denmark]);
    writeln("Switzerland:", Names[Switzerland]);
}