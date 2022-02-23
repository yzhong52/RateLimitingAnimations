# Animations with Manim

Export environment without prefix: https://stackoverflow.com/a/41274348/1035008

```
conda env export | grep -v "^prefix: " > environment.yml
```

Generate animation for rate limiting:

```
manim -pql rate_limit.py RateLimit
```

```
manim -pql rate_limit.py TokenBucketScene --format=gif
manim -pql rate_limit.py FixWindowScene --format=gif
```