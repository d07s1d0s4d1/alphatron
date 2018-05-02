import alpha_stream
import db_handler

# sendingID = 58189 - valid alpha
# sendingID = 49825 - valid alpha

def print_sending_result_list(alpha_stream):
	for i, alpha in enumerate(alpha_stream.sending_result_list):
		print  i, 'alpha in stream:', alpha.params, '\n'

AS = alpha_stream.AlphaStream(sendingID = 58189) # create alpha stream with first alpha(sendingID = 58189)

AS.add(49825) # adding alpha in stream

print_sending_result_list(AS)

for i, alpha in enumerate(AS.sending_result_list):
	print 'List after', i, 'removing:'
	print_sending_result_list(AS)
	AS.remove_last()

print 'Stream after removing:'
print_sending_result_list(AS)