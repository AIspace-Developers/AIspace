#To be run in a Jupyter Notebook
import jinja2
from IPython.display import display, Javascript, HTML
import json
from json import JSONDecodeError

def setup(problemStr):

    #Create html div to target visualizations
    display(HTML("""
	<div id="field_d3"/>
    <div id="menu"/>
	"""))

	#Create template for viz script
    setupOriginTemplate = jinja2.Template(
	"""
	require(["d3.js"]);
    require.config({
      paths: {
        d3: "../files/d3"
      }
    });
    require(["d3", "jquery-3.1.0.js"], function(d3) {
        //Get the CSP problem and setup
		{% for i in problemString %}
			var jsonProblem =  {{ problemString }}
		{% endfor %}
        jsonProblem = JSON.parse(jsonProblem[0]);
        //jsonProblem = jsonProblem[0];
		//console.log("Current problemString: ",jsonProblem);
		$(document).ready(function(){
        });
        if (jsonProblem.hasOwnProperty("coordinates")){
            var coords = jsonProblem.coordinates; }
        
        
		//build canvas
		d3.select("#field_d3 svg").remove();
		var svg = d3.select("#field_d3").append("svg");
        if(coords){
            var width = 0;
            var height = 0;
            var node;
            for(node in coords[0]){
                if (coords[0][node][0] > width){
                    width = coords[0][node][0];
                }
                if (coords[0][node][1] > height){
                    height = coords[0][node][1];
                }
            }
            for(node in coords[1]){
                if (coords[1][node][0] > width){
                    width = coords[1][node][0];
                }
                if (coords[1][node][1] > height){
                    height = coords[1][node][1];
                }
            }
            width = width + 25;
            height = height + 25;
        } else {
            var width = 720;
            var height = 640;
        }
		
		svg.attr("width", width)
			.attr("height", height);
		
		svg.append("g").attr("id", "edges");
		svg.append("g").attr("id", "nodes");
		svg.append("g").attr("id", "conts");
		svg.append("g").attr("id", "labels");
		svg.append("g").attr("id", "domains");
        
        var forceVarList = [];
        var forceConList = []
        var forceEdgeList = [];
        
		//Create graph elements
		//-------------Nodes (variables)-------------------
        
		var nodeData = jsonProblem.nodes;
		var variables = svg.select("#nodes").selectAll("ellipse")
			.data(nodeData)
        .enter().append("ellipse")
			.attr("id", function(d) { return d.name;})
            .classed("vertex", true)
            .attr("domain", function(d) { return d.domain;})
            .style("fill", "white")
            .style("stroke", "black")
            .attr("ry", 30)
            .attr("rx", function(d){
                if (d.domain.length < 5){
                    return 30;
                } else if (d.domain.length >15){
                    return 80;
                }else {
                    return 20 + d.domain.length * 4;
                }
            });
        
        if (coords){
            d3.selectAll("ellipse")
                .attr("cx", function(d){return coords[0][d.name][0];})
                .attr("cy", function(d){return coords[0][d.name][1];});
        }
        variables.each(function(d){
            if (!coords){
                forceVarList.push({fnid: d.name, type: "varNode", baseDomain: d.domain});
            } else {
                forceVarList.push({fnid: d.name, type: "varNode", baseDomain: d.domain, x: (+this.getAttribute("cx")), y: (+this.getAttribute("cy"))});
            }
        });
        variables.data(forceVarList);
        
		//----------Constraints (consts)----------
        
		var constData = jsonProblem.constraints;
		var consts = svg.select("#conts").selectAll("rect")
			.data(constData)
		.enter().append("rect")
			.attr("id", function(d) { 
                var tId = d.string;
                tId = tId.replace(/!/g, "n").replace(/=/g, "eq").replace(/[!@#$%^&*()-+={}\[\], <>?/\\'";:]/g, "_");
                return "con_"+tId;
                })
            .attr("label", function(d){return d.string;})
            .classed("vertex", true)
            .attr("constraint", function(d){ return d.constraint; })
            .attr("nodes", function(d) { return d.nodes;})
            .style("fill", "white")
            .style("stroke", "black")
            .attr("height", 30);
            
        consts.each(function(d,i){
            if (this.getAttribute("label").length < 5){
                this.setAttribute("width", 50);
            }else {
                this.setAttribute("width", (this.getAttribute("label").length * 7) +20)
            }
            if(coords){
                this.setAttribute("x", coords[1][i][0]);
                this.setAttribute("y", coords[1][i][1]);
            }
        });
        consts.each(function(d, i){
            if (!coords){
                forceConList.push({fnid: this.id, type: "constNode"});
            } else {
                forceConList.push({fnid: this.id, type: "constNode", x: (+this.getAttribute("x")), y: (+this.getAttribute("y"))});
            }
        });
        
		//------------Edges (edges)------------
        
        consts.each(function(d){
            for (var node in d.nodes){
                d3.select("#edges").append("line")
                    .attr("id", function() { return "line-"+d.nodes[node] + "-" + d.string.replace(/!/g, "n").replace(/=/g, "eq").replace(/[!@#$%^&*()-+={}\[\], <>?/\\'";:]/g, "_");})
                    .attr("src", this.id)
                    .attr("dst", d.nodes[node])
                    .style("stroke-width", 1)
                    .style("stroke", "blue");
            }
        });
        var edges = d3.selectAll("#edges line");
        edges.each(function(d,i) {forceEdgeList.push(
            {feid: this.id, 
            source: forceVarList.length+(+findNodeIndex(this.getAttribute("src"), forceConList)), 
            target: (+findNodeIndex(this.getAttribute("dst"), forceVarList))});
        });
        edges.data(forceEdgeList);
        consts.data(forceConList);
        
        $("line").hover(function(){d3.select(this).style("stroke-width", 5);}, function(){d3.select(this).style("stroke-width", 1);});
		$("ellipse").hover(
            function(){
                d3.select(this).style("fill", "black");
                d3.select("#"+this.id+"-label").style("fill", "white");
                d3.select("#"+this.id+"-domain").style("fill", "white");
            }, function(){
                d3.select(this).style("fill", "white");
                d3.select("#"+this.id+"-label").style("fill", "black");
                d3.select("#"+this.id+"-domain").style("fill", "black");
            } );
        $("rect").hover(
            function(){
                d3.select(this).style("fill", "black");
                d3.select("#"+this.id+"-label").style("fill", "white");
            }, function(){
                d3.select(this).style("fill", "white");
                d3.select("#"+this.id+"-label").style("fill", "black");
                
            } );

        //------------Force Layout (setup)------------
        
        var renderIt = 1;
        function render(){
            renderIt += 1;
            variables
                .attr("cx", function(d){return d.x;})
                .attr("cy", function(d){return d.y;});
            consts
                .attr("x", function(d) {return d.x-(this.getAttribute("width")/2);})
                .attr("cx", function(d) {return d.x;})
                .attr("y", function(d) {return d.y-15;})
                .attr("cy", function(d) {return d.y+15;});
            edges
                .attr("x1", function(d){return d.source.x})
                .attr("y1", function(d){return d.source.y})
                .attr("x2", function(d){return d.target.x})
                .attr("y2", function(d){return d.target.y});
        }
        
        function boundaryForce(){
            for (var i = 0, n = forceSim.nodes().length, node, top, side; i < n; ++i) {
                node = forceSim.nodes()[i];
                if (node.type == "varNode"){
                    side = node.baseDomain.length*8;
                    top = 35;
                }
                else {
                    side = node.fnid.length*6;
                    top = 20;
                }
                if (node.x + node.vx > width-side) {
                    node.x = width-side;
                    node.vx = 0;
                    //console.log("Too far right", node, side);
                }
                if (node.x + node.vx < side) {
                    node.x = side;
                    node.vx = 0;
                }
                if (node.y + node.vy > height-top) {
                    node.y = height-top;
                    node.vy = 0;
                }
                if (node.y + node.vy < top) {
                    node.y = top;
                    node.vy = 0;
                }
            }
        }

        //--------- Force Layout (forceSim)--------
        
        var forceSim = d3.forceSimulation()
            .nodes(forceVarList.concat(forceConList))
            .velocityDecay(0.6)
            .force("gravity", d3.forceCenter(width/2, height/2))
            .force("collision", d3.forceCollide(75))
            .force("boundaries", boundaryForce)
            .alpha(0.2)
            .on("tick", render)
            .on("end", function() {
                console.log("Force layout ended");
                //--------- Draw labels and domains --    
                variables.each( function(){
                    printLabel(this.id, this.id);
                    printDomain(this.id, this.getAttribute("domain"));
                });
                consts.each( function(){
                    printLabel(this.id, this.getAttribute("label"));
                });
            })
            .stop();
        
        if (!coords) {
            recentreFlag = 1;
            forceSim
                .force("spring", d3.forceLink(forceEdgeList).distance(35).strength(0.6))
                .force("charge", d3.forceManyBody().strength(-3500))
                .restart();
        } else {
            recentreFlag = 0;
            forceSim
                .force("spring", d3.forceLink(forceEdgeList).distance(35).strength(0.0))
                .alpha(0.2)
                .alphaMin(0.1)
                .restart();
        }
        
        //-------- Drag (dragger)-------
        var dragger = d3.drag()
        .on("start", function(){
            d3.event.subject.active = true;
            forceSim.stop()
        })
        .on("drag", function() {
            d3.event.subject.x = d3.event.x;
            d3.event.subject.y = d3.event.y;
            render();
            if (d3.event.subject.type == "varNode"){
                printDomain(d3.event.subject.fnid, d3.select("#"+d3.event.subject.fnid).attr("domain"));
                printLabel(d3.event.subject.fnid, d3.event.subject.fnid);
            } else {
                printLabel(d3.event.subject.fnid, d3.select("#"+d3.event.subject.fnid).attr("label"));
            }

        })
        .on("end", function() {
            d3.event.subject.active = false;
            if(recentreFlag == 1){
                forceSim.restart();
            }
        });
        var vertices = d3.selectAll(".vertex");
        vertices.call(dragger);
        
        //----------- Menu Bar
        
        var recentreFlag;
        var menuDiv = d3.select("#menu");
        var recentreButton = menuDiv.append("button")
            .text("Graph Recentreing")
            .attr("id", "buttonCentre")
            .style("background-color", function(){
                if (recentreFlag == 1){
                    return "#ccc";
                } else {
                    return "rgb(221, 221, 221)";
                }
            })
            .classed("toggleButton", true)
            .on('click', function(){
                recentreFlag = (recentreFlag + 1) % 2;
                if (recentreFlag){
                    d3.select(this)
                        .style("background-color", "#ccc");
                } else {
                    d3.select(this)
                        .style("background-color", "rgb(221, 221, 221)");
                }
            });
        
        /*var tickButton = menuDiv.append("button")
            .text("tick")
            .attr("id", "buttonTick")
            .on('click', function(){
                console.log("ForceSim Lists", forceVarList, forceConList, forceEdgeList);
            });*/
        
        
        //----------- d3-using Utility functions -------
        // If I can figure out a way to include d3 in other JS src files
        // it will make this section useless. Using it for now though.
        console.log("Now entering utility functions");
        function printDomain(nId, domainArr) {
			var node = d3.select("[id='" + nId + "']");
			var nodeText = d3.select('[id="' + nId + '-domain"]');
			if (nodeText.empty()) {
				d3.select("#domains").append("text")
					.attr("x", node.attr("cx"))
					.attr("y", (+node.attr("cy"))+10)
					.text("{"+domainArr+"}")
					.attr("text-anchor", "middle")
					.attr("id", nId+"-domain");
			} else {
				nodeText
                    .attr("x", node.attr("cx"))
					.attr("y", (+node.attr("cy"))+10)
                    .text("{"+domainArr+"}");
			}
            node.attr("rx", function(){
                if (domainArr.length < 5) {
                    return 30;
                } else {
                    return domainArr.length * 7
                }
            });
		}
        function printLabel(nId, labelStr) {
			var node = d3.select('[id="' + nId + '"]');
			var nodeText = d3.select('[id="' + nId + '-label"]');
			if (nodeText.empty()) {
				d3.select("#labels").append("text")
					.attr("x", node.attr("cx"))
					.attr("y", node.attr("cy")-10)
					.text(labelStr)
					.attr("text-anchor", "middle")
					.attr("id", nId+"-label");
			} else {
				nodeText
                    .attr("x", node.attr("cx"))
					.attr("y", node.attr("cy")-10)
                    .text(labelStr);
			}
		}
        function findNodeIndex(str, nodes){
            for (var index in nodes){
                if (nodes[index].fnid == str)
                    return index;
            }
        }
	});
	"""
	)
		
	#Call template for setup script
    display(Javascript(setupOriginTemplate.render(
    problemString=[problemStr])))
	
	#Create template for reduceDomain script
    reduceDomainTemplate = jinja2.Template(
	"""

	require.config({
      paths: {
        d3: "../files/d3"
      }
    });
    require(["d3"], function(d3) {
		//reduceDomain
        //---------
        
        //---------
		{% for n in node %}
			var nodeId = {{ node[0] }} ;
		{% endfor %}
		{% for d in domElem %}
			var dElement = {{ domElem[0] }};
		{% endfor %}

        var dElement = ""+dElement;
		var tNode = d3.select(nodeId);
		tNode.each(function(d){
            var domain = this.getAttribute("domain").split(',');
			var index = domain.indexOf(dElement);
			if (index != -1) {
                domain.splice(index, 1);
				this.setAttribute("domain", domain);
				printDomain(tNode.attr("id"), this.getAttribute("domain"));
			} else {
				console.log("element not present in domain", dElement, this.getAttribute("domain"));
			}
		});
        
        function printDomain(nId, domainArr) {
			var node = d3.select("[id='" + nId + "']");
			var nodeText = d3.select('[id="' + nId + '-domain"]');
			if (nodeText.empty()) {
				d3.select("#domains").append("text")
					.attr("x", node.attr("cx"))
					.attr("y", (+node.attr("cy"))+10)
					.text("{"+domainArr+"}")
					.attr("text-anchor", "middle")
					.attr("id", nId+"-domain");
			} else {
				nodeText
                    .attr("x", node.attr("cx"))
					.attr("y", (+node.attr("cy"))+10)
                    .text("{"+domainArr+"}");
			}
            node.attr("rx", function(){
                if (domainArr.length < 5) {
                    return 30;
                } else {
                    return domainArr.length * 7
                }
            });
		}
        function printLabel(nId, labelStr) {
			var node = d3.select('[id="' + nId + '"]');
			var nodeText = d3.select('[id="' + nId + '-label"]');
			if (nodeText.empty()) {
				d3.select("#labels").append("text")
					.attr("x", node.attr("cx"))
					.attr("y", node.attr("cy")-10)
					.text(labelStr)
					.attr("text-anchor", "middle")
					.attr("id", nId+"-label");
			} else {
				nodeText
                    .attr("x", node.attr("cx"))
					.attr("y", node.attr("cy")-10)
                    .text(labelStr);
			}
		}

	});
	"""
	)
    global reduceDomainTemp 
    reduceDomainTemp = reduceDomainTemplate
    
    restoreDomainsTemplate = jinja2.Template(
    """
        console.log("Restoring domains");

        require.config({
          paths: {
            d3: "../files/d3"
          }
        });
        require(["d3"], function(d3) {
            
            function resetNodeDomain(nodeId){
                var baseDomain
                var node = d3.select('[id="' + nodeId + '"]')
                    .attr("domain", function(d){return d.baseDomain;});
                d3.select('[id="' + nodeId + '-domain"]')
                    .text("{"+node.attr("domain")+"}")
                    .attr("x", node.attr("cx"))
					.attr("y", (+node.attr("cy"))+10);
            }
            
            var nodes = d3.selectAll("ellipse"); //each() or just . get ID and call resetND
            nodes.each(function(){
                resetNodeDomain(this.id);
            });
        });
        
    """
    )
    global restoreDomTemp
    restoreDomTemp = restoreDomainsTemplate
    
    highlightArcTemplate = jinja2.Template(
	"""

	require.config({
      paths: {
        d3: "../files/d3"
      }
    });
    require(["d3"], function(d3) {
        //---------
        
        //---------
		{% for n in node %}
			var args = {{ node }} ;
		{% endfor %}
    
    var variable = args[0];
    var constraint = args[1];
    var newStyle = args[2];

    var fCon = constraint.replace(/!/g, "n").replace(/=/g, "eq").replace(/[!@#$%^&*()-+={}\[\], <>?/\\'";:]/g, "_");
    var arc = "line-"+variable+"-"+fCon;
    //console.log("Selected arc:",arc, d3.select("#"+arc));
    if (newStyle[0] == "bold"){
        d3.select("#"+arc).style("stroke-width", 5);
    } else if (newStyle[0] == "!bold"){
        d3.select("#"+arc).style("stroke-width", 1);
    }
    if (newStyle[1] != "na") {
        d3.select("#"+arc).style("stroke", newStyle[1]);
    }
    });
    """
    )
    global highlightArcTemp
    highlightArcTemp = highlightArcTemplate
	
#nId: string identifier of an element with a domain
#dElem: integer to be removed from the domain of nId
def reduceDomain(nId, dElem):
	#Call func script
	display(Javascript(reduceDomainTemp.render(
		node=[nId],
		domElem=[dElem])))

def restoreDomains():
    display(Javascript(restoreDomTemp.render()))
    
def highlightArc(vName, cName, s1, s2):
    #print("In highlightArc-Python", s1, s2)
    display(Javascript(highlightArcTemp.render(
    node=[vName,cName,[s1,s2]])))

