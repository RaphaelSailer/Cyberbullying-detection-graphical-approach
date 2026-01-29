# src/graph_prompt.py
GRAPH_SYSTEM_PROMPT = """
You are given two inputs: (1) a detailed contextual description of a multiplayer online game moment derived from an image, and (2) a sequence of in-game or related chat messages between players and characters.
Your task is to construct a graph that represents the full situational and social context of this moment. The graph should model people (real players), characters (in-game heroes or entities), messages, and events (including in-game actions, prior history, and social incidents) as distinct nodes, and connect them with edges that capture relationships, actions, and interactions.
Begin by identifying all unique people (players), all characters they control or reference, all explicit or implicit events described in the context (for example deaths, kills, missed abilities, bans, historical incidents, or notable game state changes), and each individual message as its own node. Then, create edges to express how these nodes relate: link people to the characters they control, characters to events they participate in, and messages to both their sender and their targets.
Use directional edges whenever an action flows one way, such as a sender sending a message, a message targeting someone, a character participating in an event, or an event affecting a character. Use a consistent single direction for symmetric relationships, but use relation names that imply symmetry (for example same_team). Messages should act as intermediary nodes when useful, allowing edges like “sender → message → target(s)” and “message → referenced event,” so that the content and intent of communication is grounded in game context.
Output contract:
Return ONLY valid JSON. Do not include explanations, markdown, comments, or natural language outside the JSON.
The JSON must have exactly three top-level keys: meta, nodes, edges.

meta:
- directed (boolean)

nodes:
- array of objects, each with required fields:
  - id (string, unique)
  - t (one of: player | character | message | event | team)
- message nodes may include:
  - text (string)
- non-message nodes must NOT include text
- omit attributes rather than guessing

edges:
- array of objects, each with required fields:
  - s (source node id)
  - t (target node id)
  - r (relation type)

Allowed relation types (r):
sent, targets, replied_to, same_team, controls, is, participated_in, caused, occurred_near, prior_conflict, prior_affiliation

Rules:
- IDs must be short, unique, and used consistently.
- Every edge must reference existing node IDs.
- Do not invent entities, events, or relationships.
- If information is missing or ambiguous, omit the node/edge.

Now generate the graph JSON for the scenario below.
""".strip()
