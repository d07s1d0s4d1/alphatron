#echo $1 > config_type
#echo 'Running: ' $1
for i in {0..4..1}
do
    echo $i
    nohup python sender.py &> sender.${i}.log &
done
echo "Senders are done"
#for i in {0..50..1}
#do
    #echo $i
    #nohup python code_to_sending.py &> code_to_sending.${i}.log &
#done
#echo "Done"
