Project Title:- Surplus Food Redistribution and Waste Mitigation Network

SDG Goal:
This project supports SDG 2, Zero Hunger, and also helps SDG 12, Responsible Consumption and Production.

Problem Description:
Restaurants, grocery stores, and caterers often throw away good surplus food because they cannot quickly connect with local shelters and 
NGOs. Different foods have varying expiry dates and storage needs, which makes it hard to manage listings with a regular database. A document 
database like MongoDB handles this flexible data much better.

Architecture and Tech Stack:
The program is written in Python using PyMongo. It uses a simple command line menu in the terminal. The database runs on MongoDB Community Server or MongoDB Atlas, and MongoDB Compass is used to view the records.

Collections:
Food donations: Stores item name, category, quantity, donor name, and status like Available or Claimed.
Shelters: Stores NGO or shelter ID, name, phone number, and city.
Claims: Links a donation to an NGO so food cannot be claimed twice.
Feedback: Stores delivery ratings and comments on food condition.

Key MongoDB Features:
Schema validation: Ensures donation ID exists and quantity is always a positive number.
Indexing: Created indexes on status and category to quickly find available food.
Aggregation: Groups donations to calculate total servings saved and view donation numbers by category.