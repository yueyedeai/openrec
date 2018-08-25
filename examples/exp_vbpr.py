import os
import sys
sys.path.append(os.getcwd())

from openrec import ImplicitModelTrainer
from openrec.utils import Dataset
from openrec.recommenders import VBPR
from openrec.utils.evaluators import AUC, Recall
from openrec.utils.samplers import VBPRPairwiseSampler
from openrec.utils.samplers import VBPREvaluationSampler
import dataloader

raw_data = dataloader.load_tradesy()
dim_user_embed = 50
dim_item_embed = 25
total_it = int(1e5)
batch_size = 1000
eval_it = 10
save_it = eval_it

train_dataset = Dataset(raw_data['train_data'], raw_data['max_user'], raw_data['max_item'], name='Train')
val_dataset = Dataset(raw_data['val_data'], raw_data['max_user'], raw_data['max_item'], name='Val', num_negatives=200)
test_dataset = Dataset(raw_data['test_data'], raw_data['max_user'], raw_data['max_item'], name='Test', num_negatives=200)

train_sampler = VBPRPairwiseSampler(batch_size=batch_size, dataset=train_dataset, 
                                      item_vfeature=raw_data['item_features'], num_process=5)
val_sampler = VBPREvaluationSampler(batch_size=batch_size, dataset=val_dataset,
                               item_vfeature=raw_data['item_features'])
test_sampler = VBPREvaluationSampler(batch_size=batch_size, dataset=test_dataset,
                                item_vfeature=raw_data['item_features'])

_, dim_v = raw_data['item_features'].shape

model = VBPR(batch_size=batch_size, 
             dim_v=dim_v, 
             total_users=train_dataset.total_users(), 
             total_items=train_dataset.total_items(), 
             dim_user_embed=dim_user_embed, 
             dim_item_embed=dim_item_embed, 
             save_model_dir='vbpr_recommender/', 
             l2_reg_embed=0.001,
             l2_reg_mlp=0.001,
             train=True, serve=True)

def dum_eval_func(model, batch_data):
    return range(len(batch_data))
model_trainer = ImplicitModelTrainer(model=model, eval_it_func=dum_eval_func)

auc_evaluator = AUC()
recall_evaluator = Recall(recall_at=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100])  
model_trainer.train(total_it=total_it, eval_it=eval_it, save_it=save_it, train_sampler=train_sampler,
                    eval_samplers=[val_sampler, test_sampler], evaluators=[auc_evaluator, recall_evaluator])

# model = VisualBPR(batch_size=batch_size, max_user=raw_data['max_user'], max_item=raw_data['max_item'], l2_reg=0.001, l2_reg_mlp=0.001, 
#         dropout_rate=0.5, dim_embed=50, item_f_source=raw_data['item_features'], dims=[1028, 128, 50], sess_config=sess_config, opt='Adam')
# sampler = PairwiseSampler(batch_size=batch_size, dataset=train_dataset, num_process=5)
# model_trainer = ImplicitModelTrainer(batch_size=batch_size, test_batch_size=test_batch_size, item_serving_size=item_serving_size,
#     train_dataset=train_dataset, model=model, sampler=sampler)

# auc_evaluator = AUC()
# recall_evaluator = Recall(recall_at=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
# model_trainer.train(num_itr=int(1e5), display_itr=display_itr, eval_datasets=[val_dataset, test_dataset],
#                     evaluators=[auc_evaluator, recall_evaluator], num_negatives=1000)
