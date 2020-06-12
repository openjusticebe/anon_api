import graphene as g
from lib_misc import cfg_get, check_envs

ALGO_CONFIG = cfg_get({})['algorithms']


class Algorithm(g.ObjectType):
    id = g.String()
    params = g.List(g.String)
    available = g.Boolean(default_value=False)
    description = g.String(default_value='')
    url = g.String(default_value='')


class Query(g.ObjectType):
    algorithms = g.List(Algorithm)
    algorithm = g.Field(Algorithm, algo_id=g.String())

    def resolve_algorithm(root, info, algo_id):
        data = {
            'id': algo_id,
            'params': [],
        }
        return Algorithm(**data)

    def resolve_algorithms(root, info):
        output = []
        for k, data in ALGO_CONFIG.items():
            output.append({
                'id': k,
                'params': [],
                'available': check_envs(data['env_required']),
                'description': data['description'],
                'url': data['url'],
            })
        return [Algorithm(**d) for d in output]
