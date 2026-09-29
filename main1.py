import asyncio
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph,START,END,MessagesState
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_groq import ChatGroq


### run weather server .\weather.exe


load_dotenv()

### llm
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

tavily_key = os.getenv("TAVILY_API_KEY")
aviation_key=os.getenv("AVIATIONSTACK_API_KEY")

async def main():
  groq_key =os.getenv("GROQ_API_KEY")
  own_key = os.getenv("OWM_API_KEY")


  ### Connection server
  client = MultiServerMCPClient(
    {
    "weather":{
      "transport":"stdio",
      "command":r"C:\Users\A plus\OneDrive\Desktop\MCP server/mcp-openweather/mcp-weather.exe",
      "args":[],
      "env":{"OWM_API_KEY":own_key}
    },
     "calculator":{
          "transport":"stdio",
          "command":"python",
          "args":["-m","mcp_server_calculator"],
    },
    "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={tavily_key}"
        },
        "flight":{
          "transport":"stdio",
         "command": "uvx",
      "args": [
        "--python",
        "3.14",
        "aviationstack-mcp"
      ],
      "env": {
        "AVIATION_STACK_API_KEY": aviation_key
      }
    },
    "github": {
      "type": "streamble_http",
      "url": "https://api.githubcopilot.com/mcp/insiders"
    }

}
    
    
  )
  tools =await client.get_tools()


  async def call_model(state:MessagesState)  :
    response = await llm.bind_tools(tools).ainvoke(state["messages"])
    return{
      "messages":[response]
    }

  builder = StateGraph(MessagesState)
  builder.add_node("call_model",call_model)
  builder.add_node("tools",ToolNode(tools))
  builder.add_edge(START,"call_model")
  builder.add_conditional_edges("call_model",tools_condition)
  builder.add_edge("tools","call_model")


  graph = builder.compile()

  print("====Enter 1 for exists===")
  while True:
     print("Ask me any thing about weather and calculation..")
     user_input = input("You: ")

     if user_input == "1":
      print("User exists..")
      break

     print("---Agent is thinking----")
     print("----Anlayzing----")

    #### ainvoke means aysnchronous 
     result =await graph.ainvoke({
        "messages":[
          {
            "role":"user",
            "content":user_input

          }
        ]
      })
     print("Ai: ",result["messages"][-1].content)



if __name__ =="__main__":
  asyncio.run(main())

