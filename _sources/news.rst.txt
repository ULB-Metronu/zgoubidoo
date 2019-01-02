News and announcements
======================

Release of Zgoubidoo 2019.1
---------------------------

Dear friends and colleagues,

As many of you already know I started working on a Python interface for Zgoubi (the famous ray-tracing code) a couple
months ago. I feel confident that it is now mature enough to be used more widely: the first release is out!

Zgoubidoo is a Python 3 interface to Zgoubi featuring support for every Zgoubi command along with a rich high-level
interface and support for interactive use cases (Jupyter Notebook, etc.).

It is available on Github: https://github.com/chernals/zgoubidoo and for the latest stable release (“2019.1”):
https://github.com/chernals/zgoubidoo/tree/2019.1 .

Over the last couple weeks I made a large effort on the documentation and it is now available on Github pages:
https://chernals.github.io/zgoubidoo/ .

Compared to the interface from Sam (pyZgoubi) the following points are, I believe, important:

- Full support of Python 3;
- The whole library uses the type-hinting mechanism available since Python 3.5 and its extension in Python 3.7. This is
  especially useful when coding, in the library itself, or for user programs, with a fully featured IDE like PyCharm;
- Complete support of 3D geometry: 3D “surveys” are available and exploited for rich visualizations (implemented with
  matplotlib and with plotly);
- Every Zgoubi command is explicitly present in the library, there is no auto-generation mechanism. This might seem
  backward but I realized that past the first painful effort this is more modular and easier to maintain;
- A complete hierarchy of command is put in place and a major effort has been put on the extensibility: defining user
  defined commands is very easy and powerful;
- This capability is already exploited to define a complete set of elements for the IBA Proteus One system;
- The library supports running Zgoubi in parallel. In particular, when operating with a beamline (sequence) and a beam
  (collection of particles), Zgoubidoo can automatically split the beam in multiple slices, run them in a multi-core fashion and collect the results into a single data structure in the end.

I had a discussion with Sam a few months ago, it was not clear for me at the time which direction I would follow, and
it seems that there are discussions about the next steps for pyZgoubi, I would be delighted to continue those discussions and see if a collaborative effort is possible.

The focus toward the next release will be:

- A complete suite of documented examples in the form of Jupyter Notebooks;
- Better and more complete documentation;
- Support for more “physics” (beam physics algorithms and methods not present in Zgoubi or re-implemented in Zgoubidoo);
- Ideas regarding a REST interface (because I have ideas for a web interface for IBA use cases).

I would be glad to discuss how this could be used in combination with Sirepo.

Please feel free to come back with any comment or suggestion. Bug reports and contributions can be made on Github directly.

I take the opportunity to thank François for its supports over the last few months, and all the people I got a chance
to discuss the matter with during ICAP’18.

With best regards,
Cedric