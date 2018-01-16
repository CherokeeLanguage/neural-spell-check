

cat train.src.txt | sed 's/ /■/g' | sed '/\(.\)/\1 /g' > train.src.tok

th preprocess.lua -train_src ../opennmt_data/train.src.tok -train_tgt ../opennmt_data/train.tgt.tok -valid_src ../opennmt_data/valid.src.tok -valid_tgt ../opennmt_data/valid.tgt.tok -save_data ../opennmt_data/char_correction -src_seq_length 160 -tgt_seq_length 160



CUDA_VISIBLE_DEVICES=0 th train.lua -data ../opennmt_data/char_correction-train.t7 -save_model ../opennmt_data/char_correction -learning_rate_decay 0.85 -word_vec_size 100 -rnn_size 400 -layers 3 -end_epoch 80 -encoder_type brnn -residual -max_batch_size 160 -gpuid 1 -optim adam -learning_rate 0.0002