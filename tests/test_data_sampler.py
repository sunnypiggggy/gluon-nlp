import pytest
import numpy as np
from mxnet.gluon import data
from gluonnlp.data import sampler as s


N = 1000


def test_sorted_sampler():
    dataset = data.SimpleDataset([np.random.normal(0, 1, (np.random.randint(10, 100), 1, 1))
                                  for _ in range(N)])
    gt_sample_id = sorted(range(len(dataset)), key=lambda i: dataset[i].shape, reverse=True)
    sample_ret = list(s.SortedSampler([ele.shape[0] for ele in dataset]))
    for lhs, rhs in zip(gt_sample_id, sample_ret):
        assert lhs == rhs


@pytest.mark.parametrize('seq_lengths', [[np.random.randint(10, 100) for _ in range(N)],
                                         [(np.random.randint(10, 100), np.random.randint(10, 100))
                                           for _ in range(N)]])
@pytest.mark.parametrize('ratio', [0.0, 0.5])
@pytest.mark.parametrize('shuffle', [False, True])
@pytest.mark.parametrize('num_buckets', [1, 10, 100, 5000])
@pytest.mark.parametrize('bucket_scheme', [s.ConstWidthBucket(),
                                           s.LinearWidthBucket(),
                                           s.ExpWidthBucket()])
@pytest.mark.parametrize('use_average_length', [False, True])
def test_fixed_bucket_sampler(seq_lengths, ratio, shuffle, num_buckets, bucket_scheme,
                              use_average_length):
    sampler = s.FixedBucketSampler(seq_lengths,
                                   batch_size=8,
                                   num_buckets=num_buckets,
                                   ratio=ratio, shuffle=shuffle,
                                   use_average_length=use_average_length,
                                   bucket_scheme=bucket_scheme)
    # here we print sampler to cover the __repr__ func of the sampler
    print(sampler)
    total_sampled_ids = []
    for batch_sample_ids in sampler:
        total_sampled_ids.extend(batch_sample_ids)
    assert len(set(total_sampled_ids)) == len(total_sampled_ids) == N


@pytest.mark.parametrize('bucket_keys', [[1, 5, 10, 100], [10, 100], [200]])
@pytest.mark.parametrize('ratio', [0.0, 0.5])
@pytest.mark.parametrize('shuffle', [False, True])
def test_fixed_bucket_sampler_with_single_key(bucket_keys, ratio, shuffle):
    seq_lengths = [np.random.randint(10, 100) for _ in range(N)]
    sampler = s.FixedBucketSampler(seq_lengths, batch_size=8, num_buckets=None,
                                   bucket_keys=bucket_keys, ratio=ratio, shuffle=shuffle)
    print(sampler)
    total_sampled_ids = []
    for batch_sample_ids in sampler:
        total_sampled_ids.extend(batch_sample_ids)
    assert len(set(total_sampled_ids)) == len(total_sampled_ids) == N

@pytest.mark.parametrize('bucket_keys', [[(1, 1), (5, 10), (10, 20), (20, 10), (100, 100)],
                                         [(20, 20), (30, 15), (100, 100)],
                                         [(100, 200)]])
@pytest.mark.parametrize('ratio', [0.0, 0.5])
@pytest.mark.parametrize('shuffle', [False, True])
def test_fixed_bucket_sampler_with_single_key(bucket_keys, ratio, shuffle):
    seq_lengths = [(np.random.randint(10, 100), np.random.randint(10, 100)) for _ in range(N)]
    sampler = s.FixedBucketSampler(seq_lengths, batch_size=8, num_buckets=None,
                                   bucket_keys=bucket_keys, ratio=ratio, shuffle=shuffle)
    print(sampler)
    total_sampled_ids = []
    for batch_sample_ids in sampler:
        total_sampled_ids.extend(batch_sample_ids)
    assert len(set(total_sampled_ids)) == len(total_sampled_ids) == N


def test_fixed_bucket_sampler_compactness():
    samples = list(
        s.FixedBucketSampler(
            np.arange(16, 32), 8, num_buckets=2,
            bucket_scheme=s.ConstWidthBucket()))
    assert len(samples) == 2


@pytest.mark.parametrize('seq_lengths', [[np.random.randint(10, 100) for _ in range(N)],
                                         [(np.random.randint(10, 100), np.random.randint(10, 100))
                                          for _ in range(N)]])
@pytest.mark.parametrize('mult', [10, 100])
@pytest.mark.parametrize('batch_size', [5, 7])
@pytest.mark.parametrize('shuffle', [False, True])
def test_sorted_bucket_sampler(seq_lengths, mult, batch_size, shuffle):
    sampler = s.SortedBucketSampler(sort_keys=seq_lengths,
                                    batch_size=batch_size,
                                    mult=mult, shuffle=shuffle)
    total_sampled_ids = []
    for batch_sample_ids in sampler:
        total_sampled_ids.extend(batch_sample_ids)
    assert len(set(total_sampled_ids)) == len(total_sampled_ids) == N


@pytest.mark.parametrize('num_samples', [30])
@pytest.mark.parametrize('num_parts', [3, 7])
@pytest.mark.parametrize('repeat', [1, 3])
def test_split_sampler(num_samples, num_parts, repeat):
    total_count = 0
    indices = []
    for part_idx in range(num_parts):
        sampler = s.SplitSampler(num_samples, num_parts, part_idx, repeat=repeat)
        count = 0
        for i in sampler:
            count += 1
            indices.append(i)
        total_count += count
        assert count == len(sampler)
    assert total_count == num_samples * repeat
    assert np.allclose(sorted(indices), np.repeat(list(range(num_samples)), repeat))


@pytest.mark.parametrize('num_samples', [30])
@pytest.mark.parametrize('num_parts', [3, 7])
def test_split_sampler_even_size(num_samples, num_parts):
    total_count = 0
    indices = []
    for part_idx in range(num_parts):
        sampler = s.SplitSampler(num_samples, num_parts, part_idx, even_size=True)
        count = 0
        for i in sampler:
            count += 1
            indices.append(i)
        total_count += count
        assert count == len(sampler)
        print(count)
    expected_count = int(num_samples + num_parts - 1) // num_parts * num_parts
    assert total_count == expected_count, (total_count, expected_count)


@pytest.mark.parametrize('seq_lengths', [[np.random.randint(10, 100) for _ in range(N)],
                                         [(np.random.randint(10, 100), np.random.randint(10, 100)) for _ in range(N)]])
@pytest.mark.parametrize('max_num_tokens', [200, 500])
@pytest.mark.parametrize('max_num_sentences', [-1, 5])
@pytest.mark.parametrize('required_batch_size_multiple', [1, 5])
@pytest.mark.parametrize('sort_type', ['sequential', 'max'])
@pytest.mark.parametrize('shuffle', [True, False])
@pytest.mark.parametrize('seed', [100, None])
def test_bounded_budget_sampler(seq_lengths, max_num_tokens, max_num_sentences,
                                required_batch_size_multiple, sort_type, shuffle, seed):
    sampler = s.BoundedBudgetSampler(seq_lengths, max_num_tokens, max_num_sentences,
                                     required_batch_size_multiple,
                                     sort_type=sort_type, shuffle=shuffle, seed=seed)
    print(sampler)
    total_sampled_ids = []
    for batch_sample_ids in sampler:
        total_sampled_ids.extend(batch_sample_ids)
    assert len(set(total_sampled_ids)) == len(total_sampled_ids) == N
    assert sorted(total_sampled_ids) == list(range(len(total_sampled_ids)))


@pytest.mark.parametrize('seq_lengths', [[np.random.randint(10, 100) for _ in range(N)],
                                         [(np.random.randint(10, 100), np.random.randint(10, 100)) for _ in range(N)]])
@pytest.mark.parametrize('max_num_tokens', [200, 500])
@pytest.mark.parametrize('max_num_sentences', [-1, 5])
@pytest.mark.parametrize('required_batch_size_multiple', [1, 5])
@pytest.mark.parametrize('shuffle', [True, False])
@pytest.mark.parametrize('num_parts', [1, 4])
@pytest.mark.parametrize('even_size', [False])
def test_sharded_iterator(seq_lengths, max_num_tokens, max_num_sentences,
                          required_batch_size_multiple, shuffle,
                          num_parts, even_size):
    total_sampled_ids = []
    for part_index in range(num_parts):
        # we use independent (but same) sampler to simulate multi process situation
        sampler = s.BoundedBudgetSampler(seq_lengths, max_num_tokens, max_num_sentences,
                                         required_batch_size_multiple,
                                         shuffle=shuffle, seed=100)
        sharded_iter = s.ShardedIterator(sampler, num_parts, part_index, even_size)
        print(sharded_iter)
        for batch_sample_ids in sharded_iter:
            total_sampled_ids.extend(batch_sample_ids)
    assert len(set(total_sampled_ids)) == len(total_sampled_ids) == N
    assert sorted(total_sampled_ids) == list(range(len(total_sampled_ids)))


@pytest.mark.parametrize('seq_lengths', [[np.random.randint(10, 100) for _ in range(N)],
                                         [(np.random.randint(10, 100), np.random.randint(10, 100)) for _ in range(N)]])
@pytest.mark.parametrize('max_num_tokens', [200, 500])
@pytest.mark.parametrize('max_num_sentences', [-1, 5])
@pytest.mark.parametrize('required_batch_size_multiple', [1, 5])
@pytest.mark.parametrize('shuffle', [True, False])
@pytest.mark.parametrize('num_parts', [1, 4])
@pytest.mark.parametrize('even_size', [True])
def test_sharded_iterator_even_size(seq_lengths, max_num_tokens, max_num_sentences,
                          required_batch_size_multiple, shuffle,
                          num_parts, even_size):
    total_sampled_ids = []
    first_batch_num = None
    for part_index in range(num_parts):
        batch_num = 0
        # we use independent (but same) sampler to simulate multi process situation
        sampler = s.BoundedBudgetSampler(seq_lengths, max_num_tokens, max_num_sentences,
                                         required_batch_size_multiple,
                                         shuffle=shuffle, seed=100)
        sharded_iter = s.ShardedIterator(sampler, num_parts, part_index, even_size)
        print(sharded_iter)
        for batch_sample_ids in sharded_iter:
            total_sampled_ids.extend(batch_sample_ids)
            batch_num += 1
        # assert batch num of each parts equals
        if first_batch_num is None:
            first_batch_num = batch_num
        else:
            assert first_batch_num == batch_num
    assert len(set(total_sampled_ids)) == N
