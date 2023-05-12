# Sharding Blockchain Simulator

Used to shard a randomly connected Blockchain network, and then test its security and scalability. Approaches used to shard the network:

1- Random Sharding (commited Dec 2022)

2- Genetic Algorithms (commited May 2023)


# Steps:

1- Clone the repository

2- Modify on the Sim_parametersl.json file:

  a. network_model(1:ER,2:BA) select the type of random network .. Erdos-Reiny or Barabasi-Albert
  
  b. upper_bound_adversary_fraction: this should be a value in [0,1) which represents the maximum tolerable adversary fraction in the the non-sharded version of the network (e.g. 0.5 for PoW-based or 0.33 for pBFT, etc.)
  
  c. actual_adversary_fraction_to_be_tested: this is the fraction to be simulated
  
  d. intra_shard_weight_importance: when using GA to optimize the distribution of nodes in shards, how important is it to have a minimized avg. diameter of shards? value in (0,1)
  
  e. Tolerable_number_of_GA_solution_repetitions: number of times a solution is reached before the GA optimizer terminates the searching process
  
  f. remaining values are self explanatory!
  

3- Run main.py (install any missing packages)

4- Once the simulator terminates, check the excel file generated and saved in the same directory ;)


# References:
-- Baniata, Hamza, and Attila Kertesz. "Approaches to Overpower Proof-of-Work Blockchains Despite Minority." IEEE Access 11 (2023): 2952-2967.
available at: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10006812
