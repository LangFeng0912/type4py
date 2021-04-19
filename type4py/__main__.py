from type4py import data_loaders
from type4py.utils import setup_logs_file
from libsa4py.cst_pipeline import Pipeline
from libsa4py.utils import find_repos_list
import argparse

data_loading_comb = {'train': data_loaders.load_combined_train_data, 'valid': data_loaders.load_combined_valid_data,
                     'test': data_loaders.load_combined_test_data, 'labels': data_loaders.load_combined_labels, 
                     'name': 'combined'}

data_loading_param = {'train': data_loaders.load_param_train_data, 'valid': data_loaders.load_param_valid_data,
                     'test': data_loaders.load_param_test_data, 'labels': data_loaders.load_param_labels, 
                     'name': 'argument'}

data_loading_ret = {'train': data_loaders.load_ret_train_data, 'valid': data_loaders.load_ret_valid_data,
                     'test': data_loaders.load_ret_test_data, 'labels': data_loaders.load_ret_labels, 
                     'name': 'return'}

data_loading_var = {'train': data_loaders.load_var_train_data, 'valid': data_loaders.load_var_valid_data,
                     'test': data_loaders.load_var_test_data, 'labels': data_loaders.load_var_labels, 
                     'name': 'variable'}

def extract(args):
    p = Pipeline(args.c, args.o, True, False, args.d)
    p.run(find_repos_list(args.c), args.w)

def preprocess(args):
    from type4py.preprocess import preprocess_ext_fns
    setup_logs_file(args.o, "preprocess")
    preprocess_ext_fns(args.o, args.l)

def vectorize(args):
    from type4py.vectorize import vectorize_args_ret
    setup_logs_file(args.o, "vectorize")
    vectorize_args_ret(args.o)

def learn(args):
    from type4py.learn import train
    setup_logs_file(args.o, "learn")
    if args.a:
        train(args.o, data_loading_param, args.p)
    elif args.r:
        train(args.o, data_loading_ret, args.p)
    elif args.v:
        train(args.o, data_loading_var, args.p)
    else:
        train(args.o, data_loading_comb, args.p)

def predict(args):
    from type4py.predict import test
    setup_logs_file(args.o, "predict")
    if args.a:
        test(args.o, data_loading_param)
    elif args.r:
        test(args.o, data_loading_ret)
    elif args.v:
        test(args.o, data_loading_var)
    else:
        test(args.o, data_loading_comb)

def eval(args):
    from type4py.eval import evaluate
    setup_logs_file(args.o, "eval")
    if args.a:
        evaluate(args.o, data_loading_param, {'Parameter'}, args.tp)
    elif args.r:
        evaluate(args.o, data_loading_ret, {'Return'}, args.tp)
    elif args.v:
        evaluate(args.o, data_loading_var, {'Variable'}, args.tp)
    else:
        evaluate(args.o, data_loading_comb, {'Parameter', 'Return', 'Variable'}, args.tp)

def main():
    arg_parser = argparse.ArgumentParser()
    sub_parsers = arg_parser.add_subparsers(dest='cmd')

    # Extract phase
    extract_parser = sub_parsers.add_parser('extract')
    extract_parser.add_argument('--c', '--corpus', required=True, type=str, help="Path to the Python corpus or dataset")
    extract_parser.add_argument('--o', '--output', required=True, type=str, help="Path to store processed projects")
    extract_parser.add_argument('--d', '--deduplicate', required=False, type=str, help="Path to duplicate files")
    extract_parser.add_argument('--w', '--workers', required=False, default=4, type=int, help="Number of workers to extract functions from the input corpus")
    extract_parser.add_argument('--l', '--limit', required=False, type=int, help="Limits the number of projects to be processed")
    extract_parser.set_defaults(func=extract)

    # Preprocess phase
    proprocess_parser = sub_parsers.add_parser('preprocess')
    proprocess_parser.add_argument('--o', '--output', required=True, type=str, help="Path to processed projects")
    proprocess_parser.add_argument('--l', '--limit', required=False, type=int, help="Limits the number of projects to be processed")
    proprocess_parser.set_defaults(func=preprocess)

    # Vectorize phase
    vectorize_parser = sub_parsers.add_parser('vectorize')
    vectorize_parser.add_argument('--o', '--output', required=True, type=str, help="Path to processed projects")
    vectorize_parser.set_defaults(func=vectorize)

    # Learning phase
    learning_parser = sub_parsers.add_parser('learn')
    learning_parser.add_argument('--o', '--output', required=True, type=str, help="Path to processed projects")
    learning_parser.add_argument('--c', '--combined', default=True, action="store_true", help="combined prediction task")
    learning_parser.add_argument('--a', '--argument', default=False, action="store_true", help="argument prediction task")
    learning_parser.add_argument('--r', '--return', default=False, action="store_true", help="return prediction task")
    learning_parser.add_argument('--v', '--variable', default=False, action="store_true", help="variable prediction task")
    learning_parser.add_argument('--p', '--parameters', required=False, type=str, help="Path to the JSON file of model's hyper-parameters")
    learning_parser.set_defaults(func=learn)

    # Prediction phase
    predict_parser = sub_parsers.add_parser('predict')
    predict_parser.add_argument('--o', '--output', required=True, type=str, help="Path to processed projects")
    predict_parser.add_argument('--c', '--combined', default=True, action="store_true", help="combined prediction task")
    predict_parser.add_argument('--a', '--argument', default=False, action="store_true", help="argument prediction task")
    predict_parser.add_argument('--r', '--return', default=False, action="store_true", help="return prediction task")
    predict_parser.add_argument('--v', '--variable', default=False, action="store_true", help="variable prediction task")
    predict_parser.set_defaults(func=predict)

    # Evaluation phase
    eval_parser = sub_parsers.add_parser('eval')
    eval_parser.add_argument('--o', '--output', required=True, type=str, help="Path to processed projects")
    eval_parser.add_argument('--c', '--combined', default=True, action="store_true", help="combined prediction task")
    eval_parser.add_argument('--a', '--argument', default=False, action="store_true", help="argument prediction task")
    eval_parser.add_argument('--r', '--return', default=False, action="store_true", help="return prediction task")
    eval_parser.add_argument('--v', '--variable', default=False, action="store_true", help="variable prediction task")
    eval_parser.add_argument('--tp', '--topn', default=10, type=int, help="Report top-n predictions [default n=10]")
    eval_parser.set_defaults(func=eval)

    args = arg_parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()