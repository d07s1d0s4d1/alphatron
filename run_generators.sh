#python manage.py add_gen_alpha --gen rank_product --n $1
#python manage.py add_gen_alpha --gen change_consts --n $1
#python manage.py add_gen_alpha --gen signed_power --n $1
#python manage.py add_gen_alpha --gen signed_power_of_tsrank --n $1
#python manage.py add_gen_alpha --gen tree_generator --n $1
#python manage.py add_gen_alpha --gen sum_of_scales --n $1
#nohup python manage.py run_stream_generator --n 10 &> gen.0.log &

for i in {0..4..1}
do
    echo $i
    nohup python manage.py run_stream_generator --n 1 &> gen.${i}.log &
done
echo "Generators are done"