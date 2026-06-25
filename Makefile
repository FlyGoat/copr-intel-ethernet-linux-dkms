SPECS := \
	ice-dkms.spec \
	iavf-dkms.spec \
	idpf-dkms.spec \
	i40e-dkms.spec \
	ixgbe-dkms.spec \
	ixgbevf-dkms.spec \
	igb-dkms.spec
DRIVERS := $(patsubst %-dkms.spec,%,$(SPECS))
OUTDIR ?= dist/srpm

.PHONY: validate update-upstreams srpm srpm-all $(addprefix srpm-,$(DRIVERS))

validate:
	python3 scripts/update-drivers.py --check

update-upstreams:
	python3 scripts/update-drivers.py --write

srpm:
ifndef spec
	$(error pass spec=<name>.spec, for example: make srpm spec=ice-dkms.spec)
endif
	mkdir -p "$(OUTDIR)"
	rpkg srpm --outdir "$(OUTDIR)" --spec "$(spec)"

srpm-all: $(addprefix srpm-,$(DRIVERS))

$(addprefix srpm-,$(DRIVERS)): srpm-%:
	$(MAKE) srpm spec=$*-dkms.spec
