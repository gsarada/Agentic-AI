#!/usr/bin/env python
import sys
import warnings
from dotenv import load_dotenv
from datetime import datetime

from crew import EngineeringTeam

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

requirement = """A simple account management system for a trading simulation platform.
The system should allow users to create an account, deposit funds, and withdraw funds.
The system should allow users to record that they have bought or sold shares, providing a quantity.
The system should calculate the total value of the user's portfolio, and the profit or loss from the initial deposit.
The system should be able to report the holdings of the user at any point in time.
The system should be able to report the profit or loss of the user at any point in time.
The system should be able to list the transactions that the user has made over time.
The system should prevent the user from withdrawing funds that would leave them with a negative balance, or
 from buying more shares than they can afford, or selling shares that they don't have.
 The system has access to a function get_share_price(symbol) which returns the current price of a share, and includes a test implementation that returns fixed prices for AAPL, TSLA, GOOGL."""
module_name = 'account.py'
class_name = 'account.py'

requirement1 = """ A simple sqllite based shared goal board. 
It should allow to add goals and tasks under the goal as parent
The agents should be able to claim a task and mark it complete. It should allow to list all tasks and
print the goals and tasks status as a live board refreshing the board at regular intervals. 
Also create mcp server and mcp client for the class so it can be exposed as MCP tool. 
Create a docker file so the MCP server can be deployed as a container"""
module_name1 = 'live_board.py'
class_name1 = 'live_board.py'

def run():
    """
    Run the crew.
    """
    inputs = {
        'requirements': requirement1,
        'module_name': module_name1,
        'class_name': class_name1
    }

    try:
        EngineeringTeam().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


load_dotenv(override=True)
run()
