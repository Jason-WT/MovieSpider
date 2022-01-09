from rec_by_self_v1 import RecBySelf
import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--account_id')
    parser.add_argument('--topk', type=int, default=5)
    parser.add_argument('--rate', type=float, default=0.0)
    parser.add_argument('--duration', type=float, default=2000)
    parser.add_argument('--content_type', default=None)
    parser.add_argument('--country', default=None)
    parser.add_argument('--debug', default=False)
    args = parser.parse_args()
    print(args)
    rec_obj = RecBySelf('cookies', args.account_id, args.topk, args.rate, args.duration, args.content_type, args.country, debug=args.debug)
    rec_obj.recommend()