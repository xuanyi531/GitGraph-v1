# GitGraph

Knowledge Graph for Commit History of a Git repository. "YahooNewsOnboarding" is a test example.

*Step 1:* Download and install Neo4j https://neo4j.com/ and start it.

​	Change the password of your Neo4j at ./neo4jFuncs.py.

*Step 2:* cd ./GitGraph and then clone a Git project to analyse.

e.g. git clone https://github.com/rahulrj/YahooNewsOnboarding.git

*Step 3:* **python3 main.py &lt;project_path&gt; [&lt;filtering options&gt;]**

p  - -filter pictures

a  - -filter audio

v  - -filter videos

c  - -customize 

<u>The above filtering content can be modified in filetypes.py.</u>

**e.g. python3 main.py   ./YahooNewsOnboarding/   pavc** means that you want to filter pics, audio, videos and some customized filetypes.

**e.g. python3 main.py   ./YahooNewsOnboarding/   pa**  means that you want to filter pictures and audio files.


*Step 4:* View the knowledge graph at http://localhost:7474

- Remember to change the default settings of Initial Node Display to show more Nodes.

- Use the Cypher statement "**MATCH p=()-->() RETURN p**" to show all the Nodes and Relationships.

- You can change the color of Nodes and Relationships as you like with Neo4j.

- If you wanna check a specific class like "MainActivity", use "**MATCH (b:Class) WHERE b.class_name="class MainActivity" RETURN b**" .

  You just need to double-click on the node to see other nodes and relationships associated with it.

![Alt text](https://github.com/carol233/picbed/raw/master/TIM%E5%9B%BE%E7%89%8720181113214428.png)

