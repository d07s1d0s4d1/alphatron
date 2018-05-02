top_configs = {
	'top': {
		'top_table_name': 'top',
		'corr': 1, 
		'min_fitness': 0.94,
		'max_top': 2000,
		'submission': True,
	}, 
	'top_gen': {
		'top_table_name': 'top_for_generators',
		'corr': 1,
		'min_fitness': 0.94,
		'max_top': 2000,
		'submission': True,
	},
}

def get_top_config(config_name):
 	return top_configs[config_name]

def get_name_list_of_top_tables():
	return top_configs.keys()